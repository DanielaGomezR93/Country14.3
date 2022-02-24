# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime, timedelta, date

class StatusPartnerController(http.Controller):

    @http.route('/country_qr_scanner/get_status_partner', type='json',auth="user", website=True, csrf=False)
    def get_status_partner(self, **kw):
        if kw.get('code'):
            res = http.request.env['res.partner'].sudo()._patameter_state_partner(kw.get("code"))
            if res.state_action == 'active':
                return {"status": "Activo",
                        "success":True,
                        "name": res.name,
                        "vat": res.prefix_vat + res.vat,
                        "photo": res.image_1920,
                        }
            else:
                return {"status": "Inactivo",
                        "success":False,
                        "name": res.name,
                        "vat": res.prefix_vat + res.vat,
                        "photo": res.image_1920,
                        }
        else:
            return {"status":"No hay codigo", "success":False}

    @http.route('/country_qr_scanner/get_status_registration_event', type='json', auth="user", website=True, csrf=False)
    def get_status_registration_event(self, **kw):
        if kw.get('code'):
            res = http.request.env['event.registration'].sudo()._patameter_state_registration_event(kw.get("code"))
            if res.state == 'open':
                if kw.get("code"):
                    search_type = kw.get("code").find("INV")
                    code_id = kw.get("code")[:search_type]
                    data = http.request.env['event.registration'].search(
                        [('id', '=', code_id)], limit=1)
                    if data.id:
                        data.action_set_done()
                        data.write({'date_scanned': datetime.now()})
                return {"status": 'Pago Confirmado',
                        "success": True,
                        "partner": res.partner_id.name,
                        "name": res.name,
                        "vat": res.prefix_vat + res.vat,
                        "photo": res.partner_id.image_1920,
                        "date_scanned": str(res.date_scanned)
                        }
            
            else:
                return {"status": 'Pago No Confirmado' if res.state == 'draft' else 'Invitación Cancelada' if res.state == 'cancel' else 'Asistido',
                        "success": False,
                        "partner": res.partner_id.name,
                        "name": res.name,
                        "vat": res.prefix_vat + res.vat,
                        "photo": res.partner_id.image_1920,
                        "date_scanned": str(res.date_scanned)
                        }
        else:
            return {"status": "No hay codigo", "success": False}
