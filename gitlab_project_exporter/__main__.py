import logging

from .server import create_app

LOG = logging.getLogger(__name__)
LOG.info("Starting gitlab-projects-exporter")
app = create_app()
