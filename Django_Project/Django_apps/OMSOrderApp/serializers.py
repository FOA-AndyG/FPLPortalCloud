from rest_framework import serializers

from Django_apps.OMSOrderApp.models import OmsLabelInfo


class OmsLabelInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OmsLabelInfo
        fields = ('name', 'alias')

