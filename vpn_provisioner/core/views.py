from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from datetime import timedelta
from .models import Code, VPNCert, VPNClientConfig
from .forms import VPNForm
from .apis import PfSenseAPI
from django.db import transaction, IntegrityError
from django.db.models import F
from django.views.decorators.http import require_POST
import base64
from django.utils.text import slugify
import json

# Create your views here.
@require_POST
def vpn_export_view(req):
    form = VPNForm(req.POST)
    if not form.is_valid():
        return JsonResponse({"success": False, "error": form.errors, "step": "Form Checking"}, status=400)
    username = form.cleaned_data['username']
    req_code = form.cleaned_data['code']
    password = form.cleaned_data['password']
    
    #verify the code
    code = Code.objects.filter(code=req_code).first()
    if not code or code.expires_at < timezone.now():
        return JsonResponse({"success": False, "error":"Invalid Code", "step": "Code Checking"}, status=400)

    lan = code.lan
    api = PfSenseAPI()
    #check if the user exists
    usercert = VPNCert.objects.filter(
        username=username,
        lan=lan,
    ).first()
    if not usercert:
        try:
            res = api.generate_certificate(username, code.caref)
            if not res['success']:
                raise Exception(f"Certificate Generation Failed {res['error']}")
            data = res['data']
            refid = data.get('refid')
            crt = data.get('crt')
            expires_at = timezone.now() + timedelta(days=data.get('lifetime'))
            if not VPNCert.objects.filter(username=username):
                res = api.create_user(refid, username, password)
                if not res['success']:
                    raise Exception(f"User creation Failed {res['error']}")
            else:
                res = api.attach_cert_user(username, refid)
                if not res['success']:
                    raise Exception(f"Cert attachment failed: {res['error']}")
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
        
        
        with transaction.atomic():
            try:
                # save to DB
                usercert = VPNCert.objects.create(
                username = username,
                lan = lan,
                cert = crt,
                pfs_cert_refid = refid,
                expires_at = expires_at,
                )
                
                code = Code.objects.select_for_update().get(code=code.code)
                if code.max_uses <= 0:
                    return JsonResponse({"success": False, "error": "Invalid Code"}, status=403)
                
                updated = Code.objects.select_for_update().filter(code=code.code).update(max_uses=F('max_uses')-1)
                if not updated:
                    return JsonResponse({"success": False, "error": "Code Update failed"}, status=400)
                
            except IntegrityError:
                return JsonResponse({"success": False, "error": "Concurrency error, retry"}, status=409)
            except Exception as e:
                return JsonResponse({"success": False, "error": "Internal Server error", "logging": str(e)}, status=500)
    
    config = VPNClientConfig.objects.filter(username=username, lan=lan).first()
    if not config:
        try:
            res = api.generate_client_config(lan.id, usercert.pfs_cert_refid, username)
            with transaction.atomic():
                config = VPNClientConfig.objects.create(
                    conf_id=res['data']['id'],
                    username=username,
                    lan=lan,
                    certref=usercert.pfs_cert_refid,
                )
        except Exception as e:
            return JsonResponse({"success": False, "error":str(e), "step": "Generate Client Config"}, status=400)
    
    try:
        res = api.export_client(lan.id, usercert.pfs_cert_refid, username, config.conf_id)
    except Exception as e:
        return JsonResponse({"success": False, "error":str(e), "step": "Export Client"}, status=400)
    if not res['success']:
        return JsonResponse({"success": False, "error":res['error'], "step": "Export Client"}, status=400)
        
    jdata = json.loads(res['file'].decode())
    binary = jdata['data']['binary_data']
    
    lines = binary.splitlines()
    clean_lines = []
    for l in lines:
        l = l.strip()
        if not l.startswith('pfSense-'):
            clean_lines.append(l)
    config_text = '\n'.join(clean_lines)
    safe_name = slugify(username) + slugify(lan.name) or "vpn"
    from io import BytesIO
    buf = BytesIO(config_text.encode())
    resp = FileResponse(buf, as_attachment=True, filename=f"{safe_name}.ovpn", content_type="application/x-openvpn-profile")
    return resp
    
def index_view(req):
    return render(req, "core/index.html", context={
        "form": VPNForm()
    })
    