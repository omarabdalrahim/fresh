odoo.define('hr_attendance.my_attendances', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var field_utils = require('web.field_utils');

const session = require('web.session');

var MyAttendances = AbstractAction.extend({
    contentTemplate: 'HrAttendanceMyMainMenu',
    events: {
        "click .o_hr_attendance_sign_in_out_icon": _.debounce(function() {
            this.update_attendance();
        }, 200, true),
    },

    willStart: function () {
        var self = this;

        var def = this._rpc({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', this.getSession().uid]], ['attendance_state', 'name', 'hours_today']],
                context: session.user_context,
            })
            .then(function (res) {
                self.employee = res.length && res[0];
                if (res.length) {
                    self.hours_today = field_utils.format.float_time(self.employee.hours_today);
                }
            });

        return Promise.all([def, this._super.apply(this, arguments)]);
    },

    update_attendance: function () {
        var self = this;
        this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                context: session.user_context,
            })
            .then(function(result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.displayNotification({ title: result.warning, type: 'danger' });
                }else if(result.view_id){
                console.log('result.view_id')
                console.log(result.view_id)
                  self.do_action({
            name: 'برجاء التحقق من',
            type: 'ir.actions.act_window',
            res_model: 'audit.attendance', // Module name goes here
            target: 'new',
            view_mode: 'form',
            context: {'default_next_action': result.next_action,'default_check_ids':result.checks},
//            view_id: result.view_id,
            views:[ [result.view_id, 'form']], // data[1] variable contains the view id
                    });
                }
            });
    },
});

core.action_registry.add('hr_attendance_my_attendances', MyAttendances);

return MyAttendances;

});
