from weasyprint import HTML

from django.template.response import TemplateResponse
from django.conf import settings


class HTML2PDFResponse(TemplateResponse):
    def __init__(self, request, template, context=None, filename=None,
                 content_type='application/pdf', status=None, charset=None, using=None):
        super().__init__(request, template, context, content_type, status, charset, using)

        if filename:
            self['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
        else:
            self['Content-Disposition'] = 'attachment'

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        content = template.render(context, self._request).encode('utf-8')
        if hasattr(settings, 'WEASYPRINT_BASEURL'):
            base_url = settings.WEASYPRINT_BASEURL
        else:
            base_url = self._request.build_absolute_uri()
        return HTML(string=content, base_url=base_url).write_pdf()
