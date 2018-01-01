import json
from datetime import datetime, timedelta


def gen_msg(hb = '', tmhp_up = True):
    msg = {}
    msg['heartbeat'] = datetime.utcnow().isoformat() if hb == '' else hb
    msg['tmhp_up'] = tmhp_up 
    msg['alerts'] = {}
    return msg

def gen_mds_batches():
   return [ \
      {'uid': 1, 'filename': 'FirstMDS.zip', 'upload_date': '20171212'}, \
      {'uid': 2, 'filename': 'SecondMDS.zip', 'upload_date': '20171112'}]

def gen_pbj_batches():
   return [ \
      {'uid': 1, 'filename': 'FirstPBJ.zip', 'upload_date': '20171212'}, \
      {'uid': 2, 'filename': 'SecondPBJ.zip', 'upload_date': '20171112'}]

def gen_overdue_reports():
   return [ \
      {'uid': 1, 'report_type': 'Five Star Report', 'upload_date': '20171212'}, \
      {'uid': 2, 'report_type': 'Crazy Report', 'upload_date': '20171112'}]

def gen_cfs_forms():
   return [ \
      {'uid': 1, 'form_type': 'ltcmi', 'upload_date': '20171212'}, \
      {'uid': 2, 'form_type': '3618', 'upload_date': '20171212'}]

#### START TEST MESSAGES ####
msgs = {}
msgs['no_alert'] = json.dumps(gen_msg())
msgs['tmhp_down'] = json.dumps(gen_msg(tmhp_up = False))
msgs['hb_lag'] = \
   json.dumps(gen_msg(hb = (datetime.utcnow() - timedelta(minutes=10)).isoformat()))

# MDS Batches Alert
msg = gen_msg()
msg['alerts']['mds_batches'] = gen_mds_batches()
msgs['alert_mds_batches'] = json.dumps(msg)

# PBJ Batches Alert
msg = gen_msg()
msg['alerts']['pbj_batches'] = gen_pbj_batches()
msgs['alert_pbj_batches'] = json.dumps(msg)

#  Overdue Reports
msg = gen_msg()
msg['alerts']['overdue_reports'] = gen_overdue_reports()
msgs['alert_reports'] = json.dumps(msg)

#  CFS Forms
msg = gen_msg()
msg['alerts']['cfs_forms'] = gen_cfs_forms()
msgs['alert_cfs'] = json.dumps(msg)

#  MDS and CFS Alerts
msg = gen_msg()
msg['alerts']['mds_batches'] = gen_mds_batches()
msg['alerts']['cfs_forms'] = gen_cfs_forms()
msgs['alert_mds_cfs'] = json.dumps(msg)

#  All Alerts
msg = gen_msg()
msg['alerts']['mds_batches'] = gen_mds_batches()
msg['alerts']['pbj_batches'] = gen_pbj_batches()
msg['alerts']['overdue_reports'] = gen_overdue_reports()
msg['alerts']['cfs_forms'] = gen_cfs_forms()
msgs['alert_all'] = json.dumps(msg)
#### END TEST MESSAGES ####
