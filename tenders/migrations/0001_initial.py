# Generated by Django 5.2 on 2025-04-14 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TenderCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Tender Categories',
            },
        ),
        migrations.CreateModel(
            name='TenderStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('reference_number', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('budget', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submission_deadline', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tenders', to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(related_name='tenders', to='tenders.tendercategory')),
                ('current_stage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tenders', to='tenders.tenderstage')),
            ],
        ),
        migrations.CreateModel(
            name='TenderDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='tender_documents/')),
                ('is_public', models.BooleanField(default=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('tender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='tenders.tender')),
            ],
        ),
    ]
