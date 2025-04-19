from odoo import fields, models, api


class Post(models.Model):
    _inherit = 'social.post'

    @api.model
    def create(self, vals):
        res = super(Post, self).create(vals)
        if res.x_task_id:
            res.x_task_id.x_count_post += 1
            res.message_post(
                body=("Ticket is created at Post  : <a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>") % (
                    res.x_task_id.id, res.x_task_id.name))
        return res
class com(models.Model):
    _inherit = 'utm.campaign'

    @api.model
    def create(self, vals):
        res = super(com, self).create(vals)
        if res.x_task_id:
            res.x_task_id.x_count_companing += 1
            # res.message_post(
            #     body=("Ticket is created at Post  : <a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>") % (
            #         res.x_task_id.id, res.x_task_id.name))
        return res

