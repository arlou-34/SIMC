from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count
from .models import PersonRecord
from .forms import VehicularAccidentForm, InjuryForm, SuicideForm
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def person_form(request):
    accident_form = VehicularAccidentForm(prefix='accident')
    injury_form = InjuryForm(prefix='injury')
    suicide_form = SuicideForm(prefix='suicide')

    # Helper to normalize text for counting
    def normalize_text(value):
        if not value:
            return ''
        return value.strip().lower()  # lowercase and strip spaces for consistency

    if request.method == 'POST':
        # Vehicular Accident
        if 'save_accident' in request.POST:
            accident_form = VehicularAccidentForm(request.POST, prefix='accident')
            if accident_form.is_valid():
                instance = accident_form.save(commit=False)
                if instance.vehicle_type == 'OTHERS':
                    instance.v_others = request.POST.get('v_others_text', '')
                if instance.patient_type == 'OTHERS':
                    instance.p_others = request.POST.get('p_others_text', '')
                instance.save()
                messages.success(request, "Vehicular Accident record saved successfully!")
                return redirect('person_form')
            else:
                messages.error(request, "Failed to save Vehicular Accident record.")

        # Injury
        elif 'save_injury' in request.POST:
            injury_form = InjuryForm(request.POST, prefix='injury')
            if injury_form.is_valid():
                instance = injury_form.save(commit=False)
                if instance.injury_mechanism == 'OTHERS':
                    instance.i_others = request.POST.get('i_others_text', '')
                instance.save()
                messages.success(request, "Injury record saved successfully!")
                return redirect('person_form')
            else:
                messages.error(request, "Failed to save Injury record.")

        # Suicide
        elif 'save_suicide' in request.POST:
            suicide_form = SuicideForm(request.POST, prefix='suicide')
            if suicide_form.is_valid():
                instance = suicide_form.save(commit=False)
                if instance.suicide_mechanism == 'OTHERS':
                    instance.s_others = request.POST.get('s_others_text', '')
                instance.save()
                messages.success(request, "Suicide record saved successfully!")
                return redirect('person_form')
            else:
                messages.error(request, "Failed to save Suicide record.")

    # Records
    vehicular_records = PersonRecord.objects.filter(vehicle_type__isnull=False)
    injury_records = PersonRecord.objects.filter(injury_mechanism__isnull=False)
    suicide_records = PersonRecord.objects.filter(suicide_mechanism__isnull=False)

    # =========================
    # Vehicular Counts (use v_others if 'OTHERS', normalized)
    vehicle_type_count = {}
    for record in vehicular_records:
        vtype = record.vehicle_type
        if vtype == 'OTHERS' and record.v_others:
            vtype = record.v_others
        key = normalize_text(vtype)
        vehicle_type_count[key] = vehicle_type_count.get(key, 0) + 1

    patient_type_count = {}
    for record in vehicular_records:
        ptype = record.patient_type
        if ptype == 'OTHERS' and record.p_others:
            ptype = record.p_others
        key = normalize_text(ptype)
        patient_type_count[key] = patient_type_count.get(key, 0) + 1

    # Injury Counts
    injury_mechanism_count = {}
    for record in injury_records:
        mech = record.injury_mechanism
        if mech == 'OTHERS' and record.i_others:
            mech = record.i_others
        key = normalize_text(mech)
        injury_mechanism_count[key] = injury_mechanism_count.get(key, 0) + 1

    # Suicide Counts
    suicide_mechanism_count = {}
    for record in suicide_records:
        mech = record.suicide_mechanism
        if mech == 'OTHERS' and record.s_others:
            mech = record.s_others
        key = normalize_text(mech)
        suicide_mechanism_count[key] = suicide_mechanism_count.get(key, 0) + 1

    # You can keep the status counts as-is, since they are from fixed choices
    def count_choices(records, field_name, choices):
        counts = {c[0]: 0 for c in choices}
        for row in records.values(field_name).annotate(total=Count(field_name)):
            if row[field_name]:
                counts[row[field_name]] = row['total']
        return counts

    v_status_count = count_choices(vehicular_records, 'v_status', PersonRecord._meta.get_field('v_status').choices)
    i_status_count = count_choices(injury_records, 'i_status', PersonRecord._meta.get_field('i_status').choices)
    s_status_count = count_choices(suicide_records, 's_status', PersonRecord._meta.get_field('s_status').choices)

    # Gender counts
    vehicular_gender_count = {g['gender']: g['total'] for g in vehicular_records.values('gender').annotate(total=Count('gender'))}
    injury_gender_count = {g['gender']: g['total'] for g in injury_records.values('gender').annotate(total=Count('gender'))}
    suicide_gender_count = {g['gender']: g['total'] for g in suicide_records.values('gender').annotate(total=Count('gender'))}

    # Totals
    vehicular_total = vehicular_records.count()
    injury_total = injury_records.count()
    suicide_total = suicide_records.count()

    return render(request, 'census_dashboard.html', {
        'accident_form': accident_form,
        'injury_form': injury_form,
        'suicide_form': suicide_form,
        'vehicular_records': vehicular_records,
        'injury_records': injury_records,
        'suicide_records': suicide_records,
        'vehicular_total': vehicular_total,
        'injury_total': injury_total,
        'suicide_total': suicide_total,
        'vehicular_gender_count': vehicular_gender_count,
        'injury_gender_count': injury_gender_count,
        'suicide_gender_count': suicide_gender_count,
        'vehicle_type_count': vehicle_type_count,
        'patient_type_count': patient_type_count,
        'vehicular_status_count': v_status_count,
        'injury_mechanism_count': injury_mechanism_count,
        'injury_status_count': i_status_count,
        'suicide_mechanism_count': suicide_mechanism_count,
        'suicide_status_count': s_status_count,
    })


 
 # === Export Summary Records ===
def export_records(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="census_summary_report.csv"'
    writer = csv.writer(response)

    # Helper to handle 'OTHERS'
    def get_value(record, field, others_field):
        value = getattr(record, field)
        if value == 'OTHERS':
            others_value = getattr(record, others_field)
            if others_value:
                return others_value
        return value

    # === VEHICULAR ACCIDENT SUMMARY ===
    vehicular_records = PersonRecord.objects.filter(vehicle_type__isnull=False)
    writer.writerow(["Vehicular Accident Summary"])
    writer.writerow(["Category", "Type", "Total"])

    # Gender count
    veh_gender_count = {}
    for r in vehicular_records:
        veh_gender_count[r.gender] = veh_gender_count.get(r.gender, 0) + 1
    for g, total in veh_gender_count.items():
        writer.writerow(["Gender", g, total])

    # Vehicle Type count
    veh_type_count = {}
    for r in vehicular_records:
        vtype = get_value(r, 'vehicle_type', 'v_others')
        veh_type_count[vtype] = veh_type_count.get(vtype, 0) + 1
    for t, total in veh_type_count.items():
        writer.writerow(["Vehicle Type", t, total])

    # Patient Type count
    patient_count = {}
    for r in vehicular_records:
        ptype = get_value(r, 'patient_type', 'p_others')
        patient_count[ptype] = patient_count.get(ptype, 0) + 1
    for t, total in patient_count.items():
        writer.writerow(["Patient Type", t, total])

    # Status count
    status_count = {}
    for r in vehicular_records:
        status_count[r.v_status] = status_count.get(r.v_status, 0) + 1
    for s, total in status_count.items():
        writer.writerow(["Vehicular Status", s, total])

    veh_total = len(vehicular_records)
    writer.writerow([])
    writer.writerow(["Total Vehicular Accidents", "", veh_total])
    writer.writerow([])

    # === INJURY SUMMARY ===
    injury_records = PersonRecord.objects.filter(injury_mechanism__isnull=False)
    writer.writerow(["Injury Summary"])
    writer.writerow(["Category", "Type", "Total"])

    # Gender count
    inj_gender_count = {}
    for r in injury_records:
        inj_gender_count[r.gender] = inj_gender_count.get(r.gender, 0) + 1
    for g, total in inj_gender_count.items():
        writer.writerow(["Gender", g, total])

    # Injury Mechanism count
    inj_mech_count = {}
    for r in injury_records:
        mech = get_value(r, 'injury_mechanism', 'i_others')
        inj_mech_count[mech] = inj_mech_count.get(mech, 0) + 1
    for m, total in inj_mech_count.items():
        writer.writerow(["Injury Mechanism", m, total])

    # Status count
    inj_status_count = {}
    for r in injury_records:
        inj_status_count[r.i_status] = inj_status_count.get(r.i_status, 0) + 1
    for s, total in inj_status_count.items():
        writer.writerow(["Injury Status", s, total])

    inj_total = len(injury_records)
    writer.writerow([])
    writer.writerow(["Total Injuries", "", inj_total])
    writer.writerow([])

    # === SUICIDE SUMMARY ===
    suicide_records = PersonRecord.objects.filter(suicide_mechanism__isnull=False)
    writer.writerow(["Suicide Summary"])
    writer.writerow(["Category", "Type", "Total"])

    # Gender count
    suc_gender_count = {}
    for r in suicide_records:
        suc_gender_count[r.gender] = suc_gender_count.get(r.gender, 0) + 1
    for g, total in suc_gender_count.items():
        writer.writerow(["Gender", g, total])

    # Suicide Mechanism count
    suc_mech_count = {}
    for r in suicide_records:
        mech = get_value(r, 'suicide_mechanism', 's_others')
        suc_mech_count[mech] = suc_mech_count.get(mech, 0) + 1
    for m, total in suc_mech_count.items():
        writer.writerow(["Suicide Mechanism", m, total])

    # Status count
    suc_status_count = {}
    for r in suicide_records:
        suc_status_count[r.s_status] = suc_status_count.get(r.s_status, 0) + 1
    for s, total in suc_status_count.items():
        writer.writerow(["Suicide Status", s, total])

    suc_total = len(suicide_records)
    writer.writerow([])
    writer.writerow(["Total Suicides", "", suc_total])
    writer.writerow([])

    # === GRAND TOTAL ===
    grand_total = veh_total + inj_total + suc_total
    writer.writerow(["GRAND TOTAL", "", grand_total])

    return response



from django.utils import timezone

# === Export vehicular Records ===
def export_vehicular_records(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicular_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date", "Age", "Gender", "Vehicle Type", "Patient Type", "Referred", "Status"])

    vehicular_records = PersonRecord.objects.filter(vehicle_type__isnull=False)

    for i, record in enumerate(vehicular_records, start=1):
        local_time = "'" + timezone.localtime(record.date_recorded).strftime("%Y-%m-%d %I:%M %p")


        writer.writerow([
            i,
            local_time,
            record.age,
            record.gender,
            record.vehicle_type if record.vehicle_type != "OTHERS" else record.v_others,
            record.patient_type if record.patient_type != "OTHERS" else record.p_others,
            record.v_referred,
            record.v_status
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", "", "", vehicular_records.count()])
    return response


# === Export Injury Records ===
def export_injury_records(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="injury_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date", "Age", "Gender", "Injury Mechanism", "Referred", "Status"])

    injury_records = PersonRecord.objects.filter(injury_mechanism__isnull=False)

    for i, record in enumerate(injury_records, start=1):
        local_time = "'" + timezone.localtime(record.date_recorded).strftime("%Y-%m-%d %I:%M %p")

        writer.writerow([
            i,
            local_time,
            record.age,
            record.gender,
            record.injury_mechanism if record.injury_mechanism != "OTHERS" else record.i_others,
            record.i_referred,
            record.i_status
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", "", injury_records.count()])
    return response



# === Export Suicide Records ===
def export_suicide_records(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="suicide_records.csv"'
    writer = csv.writer(response)

    writer.writerow(["No.", "Date", "Age", "Gender", "Suicide Mechanism", "Referred", "Status"])

    suicide_records = PersonRecord.objects.filter(suicide_mechanism__isnull=False)

    for i, record in enumerate(suicide_records, start=1):
        local_time = "'" + timezone.localtime(record.date_recorded).strftime("%Y-%m-%d %I:%M %p")


        writer.writerow([
            i,
            local_time,
            record.age,
            record.gender,
            record.suicide_mechanism if record.suicide_mechanism != "OTHERS" else record.s_others,
            record.s_referred,
            record.s_status
        ])

    writer.writerow([])
    writer.writerow(["Total", "", "", "", "", "", suicide_records.count()])
    return response



from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm

def login_view(request):
    # Only redirect if already logged in AND trying to access home, NOT login page
    if request.user.is_authenticated and request.path != '/login/':
        return redirect('person_form')

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('person_form')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")




from django.shortcuts import render, get_object_or_404, redirect
from .models import PersonRecord

def edit_vehicular_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    if request.method == "POST":
        record.age = request.POST.get('age')
        record.gender = request.POST.get('gender')

        # Vehicle Type
        vehicle_type = request.POST.get('vehicle_type')
        if vehicle_type == "OTHERS":
            record.vehicle_type = "OTHERS"
            record.v_others = request.POST.get('v_others')
        else:
            record.vehicle_type = vehicle_type
            record.v_others = ""

        # Patient Type
        patient_type = request.POST.get('patient_type')
        if patient_type == "OTHERS":
            record.patient_type = "OTHERS"
            record.p_others = request.POST.get('p_others')
        else:
            record.patient_type = patient_type
            record.p_others = ""

        # Referred
        record.v_referred = request.POST.get('v_referred')

        # Facility
        record.v_facility = request.POST.get('v_facility')

        # Status
        record.v_status = request.POST.get('v_status')

        record.save()
        return redirect('person_form')  # redirect to the list page

    return render(request, 'edit_vehicular_record.html', {'record': record})



def edit_injury_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    if request.method == "POST":
        record.age = request.POST.get('age')
        record.gender = request.POST.get('gender')

        
        injury_mechanism = request.POST.get('injury_mechanism')
        if injury_mechanism == "OTHERS":
            record.injury_mechanism = "OTHERS"
            record.i_others = request.POST.get('i_others')
        else:
            record.injury_mechanism = injury_mechanism
            record.i_others = ""

        # Referred
        record.i_referred = request.POST.get('i_referred')

        # Facility
        record.i_facility = request.POST.get('i_facility')

        # Status
        record.i_status = request.POST.get('i_status')

        record.save()
        return redirect('person_form')  # redirect to the list page

    return render(request, 'edit_injury_record.html', {'record': record})



def edit_suicide_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    if request.method == "POST":
        record.age = request.POST.get('age')
        record.gender = request.POST.get('gender')

        
        suicide_mechanism = request.POST.get('suicide_mechanism')
        if suicide_mechanism == "OTHERS":
            record.suicide_mechanism = "OTHERS"
            record.s_others = request.POST.get('s_others')
        else:
            record.suicide_mechanism = suicide_mechanism
            record.s_others = ""

        # Referred
        record.s_referred = request.POST.get('s_referred')

        # Facility
        record.s_facility = request.POST.get('s_facility')

        # Status
        record.s_status = request.POST.get('s_status')

        record.save()
        return redirect('person_form')  # redirect to the list page

    return render(request, 'edit_suicide_record.html', {'record': record})

def delete_vehicular_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    record.delete()
    return redirect('person_form')  # redirect after deletion



def delete_injury_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    record.delete()
    return redirect('person_form')  # redirect after deletion


def delete_suicide_record(request, id):
    record = get_object_or_404(PersonRecord, id=id)
    record.delete()
    return redirect('person_form')  # redirect after deletion




from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def bulk_delete_vehicular(request):
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        if ids:
            id_list = ids.split(",")
            PersonRecord.objects.filter(id__in=id_list).delete()
    return redirect('person_form')  # or your vehicular records page

@csrf_exempt
def bulk_delete_injury(request):
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        if ids:
            id_list = ids.split(",")
            PersonRecord.objects.filter(id__in=id_list).delete()
    return redirect('person_form')  # or your injury records page

@csrf_exempt
def bulk_delete_suicide(request):
    if request.method == "POST":
        ids = request.POST.get("ids", "")
        if ids:
            id_list = ids.split(",")
            PersonRecord.objects.filter(id__in=id_list).delete()
    return redirect('person_form')  # or your suicide records page