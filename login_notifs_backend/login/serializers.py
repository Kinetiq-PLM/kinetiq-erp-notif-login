# admin/serializers.py
from rest_framework import serializers
from .models import User

class LoginResponseSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    access_level = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['employee_id', 'full_name', 'email', 'modules', 'access_level']
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_modules(self, obj):
        if obj.role:
            return obj.role.get_modules_list()
        return []
    
    def get_access_level(self, obj):
        if obj.role:
            return obj.role.access_level
        return None