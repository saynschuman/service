from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from backend.courses.models import Material, Course


class MaterialClientSerializer(serializers.ModelSerializer):
    """
    Сериализатор материалов курса для клиентов
    """

    class Meta:
        model = Material
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    """
    Сериализатор материалов курса для модераторов и выше
    """
    original_data = serializers.ReadOnlyField()

    class Meta:
        model = Material
        fields = (
            'id',
            'course',
            'title',
            'rank',
            'text',
            'video',
            'video_link',
            'pdf',
            'is_download',
            'parent',
            'original_link',
            'original_data',
        )

        # def get_fields(self):
        #     fields = super().get_fields()
        #     fields['children'] = MaterialSerializer(many=True)
        #     return fields

        # def validate(self, attrs):
        #     if not attrs.get('text') and not attrs.get('video') and not attrs.get('pdf'):
        #         raise ValidationError('Одно из этих полей должно быть заполнено: text, video, pdf')
        #     return super().validate(attrs)


def make_material_copy(course: Course, material: Material, parent: Material = None, full_copy: bool = False, course_copy_to = None):
    children = []

    if getattr(material, 'children'):
        children = material.children.all()

    original_material_id = material.pk

    materials = Material.objects.filter(course=course_copy_to)
    ranks = []

    for item in materials:
        ranks.append(item.rank)

    rank = 0 if len(ranks) == 0 else ranks[-1] + 1

    material.course = course
    material.pk = None
    material.rank = rank
    material.parent = parent
    material.save()
    if full_copy:
        material.copy_files_from_material(original_material_id)

    for item in children:
            make_material_copy(course, item, parent=material, full_copy=full_copy, course_copy_to=course_copy_to)

def make_single_copy(course: Course, material: Material, course_copy_to = None):
    materials = Material.objects.filter(course=course_copy_to)
    ranks = []

    for item in materials:
        ranks.append(item.rank)

    rank = 0 if len(ranks) == 0 else ranks[-1] + 1

    material.course = course
    material.pk = None
    material.rank = rank
    material.parent = None
    material.save()


class MaterialCopySerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    material_id = serializers.IntegerField(required=True)

    def create(self, validated_data, full_copy: bool = False):
        course = get_object_or_404(Course, pk=validated_data.get('course_id'))
        material = get_object_or_404(Material, pk=validated_data.get('material_id'))
        make_material_copy(course, material, full_copy=full_copy, course_copy_to=course)
        # material.course = course
        # material.pk = None
        # material.rank = 0
        # material.parent = None
        # material.save()
        return material

    def single_create(self, validated_data):
        course = get_object_or_404(Course, pk=validated_data.get('course_id'))
        material = get_object_or_404(Material, pk=validated_data.get('material_id'))
        make_single_copy(course, material, course_copy_to=course)
        return material

    def create_full(self, validated_data):
        material = self.create(validated_data, full_copy=True)
        print(validated_data)
        print(material.children.all())
        #original_material = get_object_or_404(Material, pk=validated_data.get('material_id'))
        #material.copy_files_from_material(original_material.id)
        return material
