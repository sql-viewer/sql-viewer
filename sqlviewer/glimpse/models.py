import uuid
from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Model(UUIDModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    version = models.CharField(max_length=128, blank=False, null=False)

    def diagrams(self):
        return Diagram.objects.filter(model=self)

    def to_json(self, shallow=False):
        data = {"id": str(self.id),
                "name": self.name,
                "version": self.version}
        if not shallow:
            raise NotImplementedError("Deep serialization not implemented")
        return data


class Diagram(UUIDModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    model = models.ForeignKey(Model)

    def layer_elements(self):
        return LayerElement.objects.filter(diagram=self).select_related()

    def connection_elements(self):
        return ConnectionElement.objects.filter(diagram=self).select_related()

    def table_elements(self):
        return TableElement.objects.filter(layer_element__diagram=self).select_related()

    def to_json(self, shallow=False):
        data = {'id': str(self.id),
                'name': self.name}
        if not shallow:
            data['layers'] = [layer.to_json() for layer in self.layer_elements()]
            data['connections'] = [conn.to_json() for conn in self.connection_elements()]
            data['data'] = {
                'tables': [tel.table.to_json() for tel in self.table_elements()],
                'foreignKeys': [cel.foreignKey.to_json() for cel in self.connection_elements()]
            }
        return data


class Table(UUIDModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    model = models.ForeignKey(Model)

    def columns(self):
        return Column.objects.filter(table=self).select_related()

    def to_json(self, shallow=False):
        data = {"id": str(self.id),
                "name": self.name,
                "comment": self.comment}
        if not shallow:
            data["columns"] = [col.to_json() for col in self.columns()]
        return data


class Column(UUIDModel):
    name = models.CharField(max_length=128, blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    table = models.ForeignKey(Table)
    is_key = models.BooleanField(default=False)
    is_auto_increment = models.BooleanField(default=False)
    is_nullable = models.BooleanField(default=False)
    is_reference = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "comment": self.comment,
            "flags": {
                "reference": self.is_reference,
                "nullable": self.is_nullable,
                "hidden": self.is_hidden,
                "autoIncrement": self.is_auto_increment,
                "key": self.is_key
            }
        }


class ForeignKey(UUIDModel):
    TYPE_COLUMN = 'column'
    TYPE_TABLE = 'table'
    TYPE_CHOICES = (
        (TYPE_COLUMN, 'column'),
        (TYPE_TABLE, 'table')
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_COLUMN)
    target_table = models.ForeignKey(Table, related_name='target_table')
    target_column = models.ForeignKey(Column, null=True, related_name='target_column')
    source_table = models.ForeignKey(Table, related_name='source_table')
    source_column = models.ForeignKey(Column, null=True, related_name='source_column')
    model = models.ForeignKey(Model)

    def to_json(self):
        return {
            "id": str(self.id),
            "type": self.type,
            "source": {
                "tableId": str(self.source_table_id),
                "columnId": str(self.source_column_id)
            },
            "target": {
                "tableId": str(self.target_table_id),
                "columnId": str(self.target_column_id)
            }
        }


class AbstractElement(UUIDModel):
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    color = models.CharField(max_length=7)

    class Meta:
        abstract = True


class LayerElement(AbstractElement):
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    diagram = models.ForeignKey(Diagram)

    def tables(self):
        return TableElement.objects.filter(layer_element=self)

    def to_json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'tables': [tab.to_json() for tab in self.tables()],
            'element': {
                'color': self.color,
                'height': self.height,
                'width': self.width,
                'x': self.pos_x,
                'y': self.pos_y
            }
        }


class TableElement(AbstractElement):
    table = models.ForeignKey(Table)
    layer_element = models.ForeignKey(LayerElement)
    collapsed = models.BooleanField(default=False)

    def to_json(self):
        return {
            'id': str(self.id),
            'tableId': str(self.table_id),
            'element': {
                'collapsed': self.collapsed,
                'color': self.color,
                'height': self.height,
                'width': self.width,
                'x': self.pos_x,
                'y': self.pos_y
            }
        }


class ConnectionElement(UUIDModel):
    DRAW_SPLIT = "split"
    DRAW_FULL = "full"
    DRAW_HIDDEN = "hidden"
    DRAW_CHOICES = (
        (DRAW_SPLIT, "split"),
        (DRAW_FULL, "full"),
        (DRAW_HIDDEN, "hidden")
    )
    diagram = models.ForeignKey(Diagram)
    foreignKey = models.ForeignKey(ForeignKey)
    draw = models.CharField(max_length=10, choices=DRAW_CHOICES, default=DRAW_FULL)

    def to_json(self):
        return {
            'id': str(self.id),
            'foreignKeyId': str(self.foreignKey_id),
            'element': {
                'draw': self.draw
            }
        }
