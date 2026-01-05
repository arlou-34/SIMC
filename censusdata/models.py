from django.db import models

class PersonRecord(models.Model):
    # Personal Information
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    date_recorded = models.DateTimeField(auto_now_add=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])

        # For Vehicular Accident
    v_others = models.CharField(max_length=100, blank=True, null=True)
    p_others = models.CharField(max_length=100, blank=True, null=True)
    # For Injury
    i_others = models.CharField(max_length=100, blank=True, null=True)
    # For Suicide
    s_others = models.CharField(max_length=100, blank=True, null=True)


    # Separate numbering per category
    vehicular_no = models.PositiveIntegerField(blank=True, null=True)
    injury_no = models.PositiveIntegerField(blank=True, null=True)
    suicide_no = models.PositiveIntegerField(blank=True, null=True)

    # Vehicular Accident
    vehicle_type = models.CharField(max_length=50, choices=[
        ('SINGLE MOTOR', 'SINGLE MOTOR'),
        ('TRICYCLE', 'TRICYCLE'),
        ('CAR', 'CAR'),
        ('TRUCK', 'TRUCK'),
        ('JEEP', 'JEEP'),
        ('OTHERS','OTHERS')
    ], blank=True, null=True)
    patient_type = models.CharField(max_length=50, choices=[
        ('DRIVER', 'DRIVER'),
        ('PASSENGER', 'PASSENGER'),
        ('PEDESTRIAN', 'PEDESTRIAN'),
        ('OTHERS','OTHERS')
    ], blank=True, null=True)
    v_referred = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True, null=True)
    v_facility = models.CharField(max_length=100, choices=[
        ('SIARGAO ISLAND MEDICAL CENTER', 'SIARGAO ISLAND MEDICAL CENTER')
    ], blank=True, null=True)
    v_status = models.CharField(max_length=10, choices=[('Recovered', 'Recovered'), ('Died', 'Died')], blank=True, null=True)

    # Injury (Non-Vehicular)
    injury_mechanism = models.CharField(max_length=50, choices=[
        ('FALLING', 'FALLING'),
        ('MAULING', 'MAULING'),
        ('STABBING', 'STABBING'),
        ('GUNSHOT', 'GUNSHOT'),
        ('EXPLOSION', 'EXPLOSION'),
        ('OTHERS','OTHERS')
    ], blank=True, null=True)
    i_referred = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True, null=True)
    i_facility = models.CharField(max_length=100, choices=[
        ('SIARGAO ISLAND MEDICAL CENTER', 'SIARGAO ISLAND MEDICAL CENTER')
    ], blank=True, null=True)
    i_status = models.CharField(max_length=10, choices=[('Recovered', 'Recovered'), ('Died', 'Died')], blank=True, null=True)

    # Suicide/Self-Harm
    suicide_mechanism = models.CharField(max_length=50, choices=[
        ('HANGING', 'HANGING'),
        ('POISONING', 'POISONING'),
        ('FIREARMS', 'FIREARMS'),
        ('SELF-IMMOLATION', 'SELF-IMMOLATION'),
        ('SUICIDE BY VEHICLE', 'SUICIDE BY VEHICLE'),
        ('OTHERS','OTHERS')
    ], blank=True, null=True)
    s_referred = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], blank=True, null=True)
    s_facility = models.CharField(max_length=100, choices=[
        ('SIARGAO ISLAND MEDICAL CENTER', 'SIARGAO ISLAND MEDICAL CENTER')
    ], blank=True, null=True)
    s_status = models.CharField(max_length=10, choices=[('Recovered', 'Recovered'), ('Died', 'Died')], blank=True, null=True)

    def save(self, *args, **kwargs):
        # Assign separate auto-numbering per type
        if self.vehicle_type and not self.vehicular_no:
            self.vehicular_no = PersonRecord.objects.filter(vehicular_no__isnull=False).count() + 1
        elif self.injury_mechanism and not self.injury_no:
            self.injury_no = PersonRecord.objects.filter(injury_no__isnull=False).count() + 1
        elif self.suicide_mechanism and not self.suicide_no:
            self.suicide_no = PersonRecord.objects.filter(suicide_no__isnull=False).count() + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} (Age: {self.age}, Gender: {self.gender})"



