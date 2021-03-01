from arbiter import Minion
from plugins.base import constants as c
from .models.tasks import Task
from .api.utils import create_task
from plugins.base.data_utils.file_utils import File

minion = Minion(host=c.RABBIT_HOST, port=c.RABBIT_PORT, user=c.RABBIT_USER,
                password=c.RABBIT_PASSWORD, queue="backend")
