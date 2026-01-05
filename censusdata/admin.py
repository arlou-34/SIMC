from django.contrib import admin
from .models import PersonRecord
from django.contrib.auth.models import Group
import csv
from django.http import HttpResponse
from django.db import models
from django.utils import timezone
from datetime import datetime, date



# === Export Vehicular Accident Records ===
def export_vehicular_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicular_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date & Time", "Age", "Gender", "Vehicle Type", "Patient Type", "Status"])

    for i, record in enumerate(queryset, start=1):

        # Localize and format date/time
        dt = record.date_recorded
        if dt:
            local_dt = timezone.localtime(dt)
            dt_str = "'" + local_dt.strftime("%m/%d/%Y  %I:%M:%S %p")
        else:
            dt_str = ""

        writer.writerow([
            i,
            dt_str,
            record.age,
            record.gender,
            record.vehicle_type if record.vehicle_type != "OTHERS" else (record.v_others or ""),
            record.patient_type if record.patient_type != "OTHERS" else (record.p_others or ""),
            record.v_status or ""
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", "", queryset.count()])
    return response


export_vehicular_csv.short_description = "Export Vehicular Records to CSV"



# === Export Injury Records ===
def export_injury_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="injury_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date & Time", "Age", "Gender", "Injury Mechanism", "Status"])

    for i, record in enumerate(queryset, start=1):

        dt = record.date_recorded
        if dt:
            local_dt = timezone.localtime(dt)
            dt_str = "'" + local_dt.strftime("%m/%d/%Y  %I:%M:%S %p")
        else:
            dt_str = ""

        writer.writerow([
            i,
            dt_str,
            record.age,
            record.gender,
            record.injury_mechanism if record.injury_mechanism != "OTHERS" else (record.i_others or ""),
            record.i_status or ""
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", queryset.count()])
    return response


export_injury_csv.short_description = "Export Injury Records to CSV"



# === Export Suicide Records ===
def export_suicide_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suicide_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date & Time", "Age", "Gender", "Suicide Mechanism", "Status"])

    for i, record in enumerate(queryset, start=1):

        dt = record.date_recorded
        if dt:
            local_dt = timezone.localtime(dt)
            dt_str = "'" + local_dt.strftime("%m/%d/%Y  %I:%M:%S %p")
        else:
            dt_str = ""

        writer.writerow([
            i,
            dt_str,
            record.age,
            record.gender,
            record.suicide_mechanism if record.suicide_mechanism != "OTHERS" else (record.s_others or ""),
            record.s_status or ""
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", queryset.count()])
    return response


export_suicide_csv.short_description = "Export Suicide Records to CSV"





# --------------------
# Admin Panel Setup
# --------------------
admin.site.unregister(Group)
admin.site.site_header = "My Health Monitoring System"
admin.site.site_title = "MHMS Admin Portal"
admin.site.index_title = "Welcome to the Monitoring Dashboard"

class BasePersonRecordAdmin(admin.ModelAdmin):
    list_display = ('id','date_recorded','age','gender')
    search_fields = ('v_others', 'p_others', 'i_others', 's_others')
    list_filter = ('gender',)

# --------------------
# Proxy Models
# --------------------
class VehicularPerson(PersonRecord):
    class Meta:
        proxy = True
        verbose_name = 'Vehicular Accident'
        verbose_name_plural = 'Vehicular Accidents'

class InjuryPerson(PersonRecord):
    class Meta:
        proxy = True
        verbose_name = 'Injury Record'
        verbose_name_plural = 'Injury Records'

class SuicidePerson(PersonRecord):
    class Meta:
        proxy = True
        verbose_name = 'Suicide Record'
        verbose_name_plural = 'Suicide Records'

# --------------------
# Admins
# --------------------
@admin.register(VehicularPerson)
class VehicularAdmin(BasePersonRecordAdmin):
    list_display = ('age', 'date_recorded', 'gender', 'get_vehicle_type', 'get_patient_type', 'v_status')
    fields = ('age', 'gender','vehicle_type', 'v_others','v_status','v_referred', 'v_facility')
    actions = [export_vehicular_csv]

    def get_vehicle_type(self, obj):
        return obj.v_others if obj.vehicle_type == 'OTHERS' and obj.v_others else obj.vehicle_type
    get_vehicle_type.short_description = 'Vehicle Type'

    def get_patient_type(self, obj):
        return obj.p_others if obj.patient_type == 'OTHERS' and obj.p_others else obj.patient_type
    get_patient_type.short_description = 'Patient Type'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(vehicle_type__isnull=False)

@admin.register(InjuryPerson)
class InjuryAdmin(BasePersonRecordAdmin):
    list_display = ('age', 'date_recorded', 'gender', 'get_injury_mechanism', 'i_status')
    fields = ('age','gender','injury_mechanism','i_others','i_status','i_referred','i_facility')
    actions = [export_injury_csv]

    def get_injury_mechanism(self, obj):
        return obj.i_others if obj.injury_mechanism == 'OTHERS' and obj.i_others else obj.injury_mechanism
    get_injury_mechanism.short_description = 'Injury Mechanism'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(injury_mechanism__isnull=False)

@admin.register(SuicidePerson)
class SuicideAdmin(BasePersonRecordAdmin):
    list_display = ('age', 'date_recorded', 'gender', 'get_suicide_mechanism', 's_status')
    fields = ('age','gender','suicide_mechanism','s_others','s_status','s_referred','s_facility')
    actions = [export_suicide_csv]

    def get_suicide_mechanism(self, obj):
        return obj.s_others if obj.suicide_mechanism == 'OTHERS' and obj.s_others else obj.suicide_mechanism
    get_suicide_mechanism.short_description = 'Suicide Mechanism'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(suicide_mechanism__isnull=False)

def export_csv(modeladmin, request, queryset, filename, field_names):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            # Format datetime fields
            if isinstance(value, (models.DateTimeField, models.DateField)):
                value = value.strftime("%Y-%m-%d %H:%M:%S") if value else ""
            row.append(value)
        writer.writerow(row)
    return response
