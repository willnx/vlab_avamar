# -*- coding: UTF-8 -*-
from flask import Flask
from celery import Celery

from vlab_avamar_api.lib import const
from vlab_avamar_api.lib.views import HealthView, AvamarView, AvamarNDMPView

app = Flask(__name__)
app.celery_app = Celery('avamar', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
app.celery_app.conf.broker_heartbeat = 0 #https://github.com/celery/celery/issues/4895

HealthView.register(app)
AvamarView.register(app)
AvamarNDMPView.register(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
