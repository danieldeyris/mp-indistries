from odoo import fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class InvoicingRun(models.Model):
    _name = "invoicing.run"
    _description = "Invoicing Run"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "date desc, id desc"

    def unlink(self):
        for run in self:
            if run.state != 'cancel':
                raise UserError(_('You cannot delete an invoicing run not un dratf state.'))
        return super(InvoicingRun, self).unlink()

    name = fields.Char(
        'Purchase Requirement',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Datetime.now()
        , copy=False
    )
    date = fields.Datetime(
        'Date',
        readonly=True, required=True,
        default=fields.Datetime.now, copy=False)

    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('process', 'In Process'),
        ('done', 'Complete'),
        ('cancel', 'Cancel')],
                             copy=False, index=True, readonly=True,
                             default='draft',
                             track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, index=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('stock.inventory'))
    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        readonly=True,
        states={'draft': [('readonly', False)]})
    amount_total = fields.Monetary(
        compute='_compute_amount_all',
        string='Total',
        readonly=True, copy=False)
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency', readonly=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        default=lambda self: self.env.user, copy=False, readonly=True)

    invoice_ids = fields.One2many('account.move', 'invoicing_run_id', string='Invoices', readonly=True, copy=False)
    invoice_count = fields.Integer("Invoice Count", compute='_compute_invoice_count')

    def _compute_invoice_count(self):
        for run in self:
            run.invoice_count = len(run.invoice_ids)

    def _compute_amount_all(self):
        for run in self:
            run.amount_total = sum(self.invoice_ids.mapped('amount_total'))

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        action['context'] = context
        return action

    def action_cancel(self):
        for run in self:
            if run.state == 'process':
                run.action_reset()
                run.state = 'cancel'
            elif run.state == 'draft':
                run.state = 'cancel'

    def action_reset(self):
        for run in self:
            for invoice in run.invoice_ids:
                invoice.unlink()
            run.state = 'draft'

    def action_confirm(self):
        for run in self:
            for invoice in run.invoice_ids:
                invoice.action_post()
            run.state = 'done'

    def action_process(self):
        for run in self:
            run.invoicing(run.date, True)

    def action_print(self):
        self.ensure_one()
        action = self.invoice_ids.action_invoice_print()
        return action

    def invoicing(self, invoicing_date=None, print_invoices=False):
       if not invoicing_date or invoicing_date == None:
           invoicing_date = fields.Date.context_today
       domain = [('invoice_status', '=', 'to invoice')]
       if self.partner_id:
           domain += [('partner_id', '=', self.partner_id.id)]
       sale_to_invoice = self.env['sale.order'].search(domain, limit=1000)
       #invoices_new = self.env['account.move']
       invoices = self.env['account.move']
       groups = set(sale_to_invoice.mapped('invoicing_mode'))
       sale_to_invoice._get_invoice_status()
       for group in groups:
           sales = sale_to_invoice.filtered(lambda inv: inv.invoicing_mode == group and inv.invoice_status == 'to invoice')
           if group == 'standard':
               invoices = sales._create_invoices(grouped=False, final=True)
           elif group == 'nogroup':
               invoices = sales._create_invoices(grouped=True, final=True)
           elif group == 'shipment':
               for order in sales:
                    if len(order.picking_ids):
                        invoice = order._create_invoices_from_pickings(final=True)
                    else:
                        invoice = order._create_invoices(final=True)
                    if len(invoice):
                        invoices |= invoice
           else:
               invoices = sales._create_invoices(final=True)
           if invoicing_date:
               invoices.invoice_date = invoicing_date
               invoices.date = invoicing_date
           invoices.invoicing_run_id = self.id
           #invoices_new |= invoices
           self._cr.commit()
       self.state = 'process'

    def batch_invoicing(self):
        run = self.env["invoicing.run"].create({
            'name': _('Auto process %s' % fields.Datetime.now()),
            'date': fields.Datetime.now(),
            'user_id': self.env.user.id,
        })
        run.action_process()
        if run.invoice_count:
            run.action_confirm()
        else:
            run.action_cancel()
            run.unlink()
