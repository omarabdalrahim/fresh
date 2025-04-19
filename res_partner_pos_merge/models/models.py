# -*- coding: utf-8 -*-

from odoo import models, fields, api
import hashlib
import  logging
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    def unlink(self):
        running_sessions = self.env['pos.session'].sudo().search([('state', '!=', 'closed')])
        check=False
        session_id=[]
        for rec in self:
            _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            _logger.info(rec)
            session_id = self.env['pos.order'].sudo().search([('partner_id','=',rec.id)])
            if session_id and session_id.state!='closed':
                check=True



        # if running_sessions and check==False:
        #     raise UserError(
        #         _("You cannot delete contacts while there are active PoS sessions. Close the session(s) %s first.")
        #         % ", ".join(session.name for session in running_sessions)
        #     )
        return super(ResPartner, self).unlink()