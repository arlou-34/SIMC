from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Main pages
    path('person-form/', views.person_form, name='person_form'),

    # Export
    path('export/', views.export_records, name='export_records'),
    path('export/vehicular/', views.export_vehicular_records, name='export_vehicular_records'),
    path('export/injury/', views.export_injury_records, name='export_injury_records'),
    path('export/suicide/', views.export_suicide_records, name='export_suicide_records'),
    path('vehicular/edit/<int:id>/', views.edit_vehicular_record, name='edit_vehicular_record'),
    path('vehicular/delete/<int:id>/', views.delete_vehicular_record, name='delete_vehicular_record'),
    path('injury/edit/<int:id>/', views.edit_injury_record, name='edit_injury_record'),
    path('injury/delete/<int:id>/', views.delete_injury_record, name='delete_injury_record'),
    path('suicide/edit/<int:id>/', views.edit_suicide_record, name='edit_suicide_record'),
    path('suicide/delete/<int:id>/', views.delete_suicide_record, name='delete_suicide_record'),
    path('vehicular/delete/bulk/', views.bulk_delete_vehicular, name='bulk_delete_vehicular'),
    path('injury/delete/bulk/', views.bulk_delete_vehicular, name='bulk_delete_injury'),
    path('suicide/delete/bulk/', views.bulk_delete_suicide, name='bulk_delete_suicide'),
    


]



