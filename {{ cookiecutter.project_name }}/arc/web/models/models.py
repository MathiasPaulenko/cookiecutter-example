import enum

from wtforms import BooleanField, IntegerField, StringField, PasswordField, FloatField

from arc.web.extensions import db


class BaseModel(db.Model):
    """
    Base model with created_on and updated_on
    """
    __abstract__ = True
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def save(self):
        db.session.add(self)
        db.session.commit()


class StatusType(enum.Enum):
    """
        Enum class for the different status values.
    """
    PASSED = 1
    FAILED = 2
    SKIPPED = 3

    def get_status_type(self, status):
        """
            Given a status string, return the value.
        :param status:
        :return:
        """
        status = status.lower()
        if status == "passed":
            return self.PASSED
        elif status == "failed":
            return self.FAILED
        else:
            return self.SKIPPED


class ScenarioType(enum.Enum):
    """
        Enum class for the different scenario types.
    """
    SCENARIO = 1
    SCENARIO_OUTLINE = 2
    BACKGROUND = 3


class DataType(enum.Enum):
    """
        Enum class for the different data types
    """
    STRING = 'string'
    INTEGER = 'int'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    PASSWORD = 'password'

    @staticmethod
    def get_data_type_by_input_type(input_type):
        if input_type == 'BooleanField':
            return DataType.BOOLEAN
        elif input_type == 'IntegerField':
            return DataType.INTEGER
        elif input_type == 'StringField':
            return DataType.STRING
        elif input_type == 'PasswordField':
            return DataType.PASSWORD
        elif input_type == 'FloatField':
            return DataType.FLOAT


class Execution(BaseModel):
    """
        Execution class with the global result of the features and scenarios and also project information.
    """
    __tablename__ = "execution"
    id = db.Column(db.Integer, primary_key=True)
    total_features = db.Column(db.Integer)
    features_passed = db.Column(db.Integer)
    features_failed = db.Column(db.Integer)
    total_scenarios = db.Column(db.Integer)
    passed_scenarios = db.Column(db.Integer)
    failed_scenarios = db.Column(db.Integer)
    total_steps = db.Column(db.Integer)
    steps_passed = db.Column(db.Integer)
    steps_failed = db.Column(db.Integer)
    steps_skipped = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    application = db.Column(db.String(25))
    business_area = db.Column(db.String(25))
    entity = db.Column(db.String(25))
    user_code = db.Column(db.String(25))
    environment = db.Column(db.String(25))
    version = db.Column(db.String(25))
    features = db.relationship('ExecutionFeature', backref='execution', lazy=True)


class ExecutionFeature(BaseModel):
    """
        This class represents a Feature with all the data generated.
    """
    __tablename__ = "execution_feature"
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.ForeignKey(Execution.id))
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    status = db.Column(
        db.Enum(StatusType, values_callable=lambda x: [str(member.value) for member in StatusType])
    )
    position = db.Column(db.Integer)
    total_scenarios = db.Column(db.Integer)
    passed_scenarios = db.Column(db.Integer)
    failed_scenarios = db.Column(db.Integer)
    total_steps = db.Column(db.Integer)
    steps_passed = db.Column(db.Integer)
    steps_failed = db.Column(db.Integer)
    steps_skipped = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    duration = db.Column(db.Float)
    os = db.Column(db.String(25))
    driver = db.Column(db.String(25))
    scenarios = db.relationship('ExecutionScenario', backref='feature', lazy=True)


class ExecutionScenario(BaseModel):
    """
        This class represents a Scenario with all the data generated.
    """
    __tablename__ = "execution_scenario"
    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.ForeignKey(ExecutionFeature.id))
    name = db.Column(db.Text())
    description = db.Column(db.Text())
    status = db.Column(
        db.Enum(StatusType, values_callable=lambda x: [str(member.value) for member in StatusType])
    )
    position = db.Column(db.Integer)
    scenario_type = db.Column(
        db.Enum(ScenarioType, values_callable=lambda x: [str(member.value) for member in ScenarioType])
    )
    total_steps = db.Column(db.Integer)
    steps_passed = db.Column(db.Integer)
    steps_failed = db.Column(db.Integer)
    steps_skipped = db.Column(db.Integer)
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    duration = db.Column(db.Float)
    steps = db.relationship('ExecutionStep', backref='scenario', lazy=True)


class ExecutionStep(BaseModel):
    """
        This class represents a Step with all the data generated.
    """
    __tablename__ = "execution_step"
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.ForeignKey(ExecutionScenario.id))
    parent_step = db.Column(db.Integer, nullable=True)
    position = db.Column(db.Integer)
    status = db.Column(
        db.Enum(StatusType, values_callable=lambda x: [str(member.value) for member in StatusType])
    )
    keyword = db.Column(db.String(25))
    name = db.Column(db.Text())
    start_time = db.Column(db.Float)
    end_time = db.Column(db.Float)
    duration = db.Column(db.Float)


class TalosSettings(BaseModel):
    """
        This class represents a settings configuration
    """
    __tablename__ = "talos_settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    active = db.Column(db.Boolean, default=False, nullable=False)
    setting_values = db.relationship('SettingsValue', cascade="all,delete", backref='settings', lazy=True)

    def get_setting_values_key_value(self):
        values = {}
        for value in self.setting_values:
            values[value.name] = value
        return values

    def get_settings_values_imported_steps(self):
        values = []
        for value in self.setting_values:
            if "keywords" in value.name:
                values.append(value)
        return values


@db.event.listens_for(TalosSettings, 'before_insert')
def before_insert_selected_default_settings(mapper, connection, target):
    """
    This is an event triggered when a Talos Settings is inserted.
    If the new setting configuration is marked as default then set all the other configuration as non default.
    :param mapper:
    :param connection:
    :param target:
    :return:
    """
    if target.active:
        link_table = TalosSettings.__table__
        connection.execute(
            link_table.update().where(link_table.c.active == 1 and link_table.c.id != target.id).values(active=0)
        )


@db.event.listens_for(TalosSettings, 'before_update')
def before_update_selected_default_settings(mapper, connection, target):
    """
    This is an event triggered when a Talos Settings is updated
    If the target setting configuration is marked as default then set all the other configuration as non default.
    :param mapper:
    :param connection:
    :param target:
    :return:
    """
    if target.active:
        link_table = TalosSettings.__table__
        connection.execute(
            link_table.update().where(link_table.c.id != target.id).values(active=0)
        )


@db.event.listens_for(TalosSettings, 'after_delete')
def after_delete_selected_default_settings(mapper, connection, target):
    """
    This is an event triggered when a Talos Settings is deleted.
    This event check if the element deleted was marked as default configuration, if so, then get the last configuration
    available and set it as default
    :param mapper:
    :param connection:
    :param target:
    :return:
    """
    if target.active:
        link_table = target.__table__
        talos_settings = TalosSettings.query.order_by(TalosSettings.id.desc()).first()
        connection.execute(
            link_table.update().where(link_table.c.id == talos_settings.id).values(active=1)
        )


class SettingsValue(BaseModel):
    """
        This class represents a settings value
    """
    __tablename__ = "settings_value"
    id = db.Column(db.Integer, primary_key=True)
    setting_id = db.Column(db.ForeignKey(TalosSettings.id))
    name = db.Column(db.Text(), nullable=False)
    data_type = db.Column(
        db.Enum(DataType, values_callable=lambda x: [str(member.value) for member in DataType])
    )
    is_custom = db.Column(db.Boolean, default=False, nullable=False)
    value = db.Column(db.String(25))


class CustomExecution(BaseModel):
    __tablename__ = "custom_execution"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    conf_properties = db.Column(db.Text())
    headless = db.Column(db.Boolean, default=False, nullable=False)
    tags = db.Column(db.Text())
    environment = db.Column(db.String())
    extra_arguments = db.Column(db.Text())
