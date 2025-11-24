from django.utils import timezone
from datetime import timedelta, datetime
from .models import VPNCert, Code
from .apis import PfSenseAPI

def renew_cert(cert):
    api = PfSenseAPI()
    crt, prv, passwd, exp_at = api.generate_certificate(cert.username)
    
    res = api.upload_cert(cert.username, crt, prv)
    new_refid = res['data']['id']
    
    api.attach_cert_user(cert.username, new_refid)
    # TODO: Update the DB and other things of necessary
    pass

def check_exp_certs():
    soon = datetime.now(timezone.utc())
    exp_certs = VPNCert.objects.filter(expires_at__lte=soon, renewed=False, need_renew=True)
    for c in exp_certs:
        # TODO: make all certs that need renew and are not renewd to renew
        pass

def delete_codes():
    # TODO: Delete all need_deleted codes
    pass

def check_needs():
    # TODO: check all codes and certs that need renewd/deleted to True
    pass