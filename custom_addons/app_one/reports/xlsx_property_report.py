import base64
import tempfile

import io
import xlsxwriter
from ast import literal_eval
from odoo import http
from odoo.http import request


class XlsxPropertyReport(http.Controller):

    @http.route('/property/excel/report/<string:property_ids>', type='http', auth="user")
    def download_property_report_excel(self, property_ids):

        properties = request.env['property'].browse(literal_eval(property_ids))
        company = request.env.company

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # ================= Formats ================================
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'align': 'center',
            'valign': 'vcenter',
            'border_color': '#FFFFFF',
            'bg_color': 'white',
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 8,
            'align': 'left',
            'border_color': '#FFFFFF',
            'text_wrap': True,
            'valign': 'top',
        })

        label_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        value_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        })

        footer_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 8,
            'border': 0,
            'bg_color': 'white',
            'text_wrap': True,
        })

        # ============ Each Sheet/Property ============
        for prop in properties:
            sheet_name = f"{prop.name}_{prop.id}"[:31]
            ws = workbook.add_worksheet(sheet_name)

            ws.set_column(0, 0, 40)
            ws.set_column(1, 1, 35)

            row = 0
            # ============ HEADER ============
            header_text = f"\n\n\n\n{company.name or ''}\n{company.city or ''}\n{company.country_id.name or ''}"

            ws.set_row(row, 100)
            ws.merge_range(row, 0, row, 1, header_text, header_format)

            if company.logo:
                logo_data = base64.b64decode(company.logo)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    tmp.write(logo_data)
                    tmp_path = tmp.name

                ws.insert_image(
                    row, 0, tmp_path,
                    {'x_scale': 0.13, 'y_scale': 0.13, 'x_offset': 11, 'y_offset': 11}
                )

            row += 1

            # ========== Title (Property Report) ==========
            ws.set_row(row, 30)
            ws.merge_range(row, 0, row, 1, "Property Report", title_format)
            row += 1
            # ========== Data Table ==========
            data_rows = [
                ('Reference', prop.ref),
                ('Name', prop.name),
                ('Postcode', prop.postcode),
                ('Date Availability', prop.date_availability),
                ('Expected Selling Date', prop.expected_selling_date),
                ('Is Late', 'Yes' if prop.is_late else 'No'),
                ('Expected Price', prop.expected_price),
                ('Selling Price', prop.selling_price),
                ('Difference', prop.diff),
                ('Bedrooms', prop.bedrooms),
                ('Living Area', prop.living_area),
                ('Facades', prop.facades),
                ('Garden', 'Yes' if prop.garden else 'No'),
                ('Garage', 'Yes' if prop.garage else 'No'),
                ('Owner', prop.owner_id.name if prop.owner_id else ''),
                ('Owner Address', prop.owner_address),
                ('Owner Phone', prop.owner_phone),
                ('Garden Area', prop.garden_area),
                ('Garden Orientation', prop.garden_orientation),
            ]

            for label, value in data_rows:
                ws.write(row, 0, label, label_format)
                ws.write(row, 1, str(value or ''), value_format)
                row += 1

            # ========== Footer =============

            footer_text = f"{company.phone or ''} | {company.email or ''}\n{company.website or ''}"

            ws.set_row(row, 60)
            ws.merge_range(row, 0, row, 1, footer_text, footer_format)

        # ============ Finalize ============
        workbook.close()
        output.seek(0)

        return request.make_response(
            output.getvalue(),

            #instructions
            headers=[
                (
                    'Content-Type',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ),
                (
                    'Content-Disposition',
                    'attachment; filename="Property_Report.xlsx"'
                ),
            ]
        )