# -*- coding: utf-8 -*-
import gazu
import pyblish.api

from ayon_kitsu.pipeline import KitsuPublishContextPlugin


class KitsuLogOut(KitsuPublishContextPlugin):
    """Log out from Kitsu API."""

    order = pyblish.api.IntegratorOrder + 10
    label = "Kitsu Log Out"

    def process(self, context):
        gazu.log_out()
