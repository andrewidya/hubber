from django.views.generic.base import TemplateView
from django.urls import re_path

urlpatterns = [
    # GRAPPELLI DOM DOCUMENTATION
    re_path(r'^grp-doc/change-form/', TemplateView.as_view(template_name='grp_doc/change_form.html'), name="grp_doc_change_form"),
    re_path(r'^grp-doc/change-list/', TemplateView.as_view(template_name='grp_doc/change_list.html'), name="grp_doc_change_list"),
    re_path(r'^grp-doc/admin-index/', TemplateView.as_view(template_name='grp_doc/admin_index.html'), name="grp_doc_admin_index"),

    re_path(r'^grp-doc/tables/', TemplateView.as_view(template_name='grp_doc/tables.html'), name="grp_doc_tables"),

    re_path(r'^grp-doc/pagination/', TemplateView.as_view(template_name='grp_doc/pagination.html'), name="grp_doc_pagination"),
    re_path(r'^grp-doc/search-form/', TemplateView.as_view(template_name='grp_doc/search_form.html'), name="grp_doc_search_form"),
    re_path(r'^grp-doc/filter/', TemplateView.as_view(template_name='grp_doc/filter.html'), name="grp_doc_filter"),
    re_path(r'^grp-doc/date-hierarchy/', TemplateView.as_view(template_name='grp_doc/date_hierarchy.html'), name="grp_doc_date_hierarchy"),

    re_path(r'^grp-doc/fieldsets/', TemplateView.as_view(template_name='grp_doc/fieldsets.html'), name="grp_doc_fieldsets"),
    re_path(r'^grp-doc/errors/', TemplateView.as_view(template_name='grp_doc/errors.html'), name="grp_doc_errors"),
    re_path(r'^grp-doc/form-fields/', TemplateView.as_view(template_name='grp_doc/form_fields.html'), name="grp_doc_form_fields"),
    re_path(r'^grp-doc/submit-rows/', TemplateView.as_view(template_name='grp_doc/submit_rows.html'), name="grp_doc_submit_rows"),

    re_path(r'^grp-doc/modules/', TemplateView.as_view(template_name='grp_doc/modules.html'), name="grp_doc_modules"),
    re_path(r'^grp-doc/groups/', TemplateView.as_view(template_name='grp_doc/groups.html'), name="grp_doc_groups"),

    re_path(r'^grp-doc/navigation/', TemplateView.as_view(template_name='grp_doc/navigation.html'), name="grp_doc_navigation"),
    re_path(r'^grp-doc/context-navigation/',
            TemplateView.as_view(template_name='grp_doc/context_navigation.html'),
            name="grp_doc_context_navigation"),

    re_path(r'^grp-doc/basic-page-structure/',
            TemplateView.as_view(template_name='grp_doc/basic_page_structure.html'),
            name="grp_doc_basic_page_structure"),

    re_path(r'^grp-doc/tools/', TemplateView.as_view(template_name='grp_doc/tools.html'), name="grp_doc_tools"),
    re_path(r'^grp-doc/object-tools/', TemplateView.as_view(template_name='grp_doc/object_tools.html'),
            name="grp_doc_object_tools"),

    re_path(r'^grp-doc/mueller-grid-system-tests/',
            TemplateView.as_view(template_name='grp_doc/mueller_grid_system_tests.html'),
            name="grp_doc_mueller_grid_system_tests"),
    re_path(r'^grp-doc/mueller-grid-system/',
            TemplateView.as_view(template_name='grp_doc/mueller_grid_system.html'),
            name="grp_doc_mueller_grid_system"),
    re_path(r'^grp-doc/mueller-grid-system-layouts/',
            TemplateView.as_view(template_name='grp_doc/mueller_grid_system_layouts.html'),
            name="grp_doc_mueller_grid_system_layouts"),

    re_path(r'^grp-doc', TemplateView.as_view(template_name='grp_doc/index.html'), name="grp_doc")
]
