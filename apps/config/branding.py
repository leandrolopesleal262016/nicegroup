class BrandingConfig:
    def __init__(self):
        self.APP_NAME = "Nice Group"
        self.APP_DESCRIPTION = "Sistema de Gestão de Imóveis"
        self.PRIMARY_COLOR = "#1572E8"
        self.SECONDARY_COLOR = "#6861CE"
        self.APP_LOGO = "/static/assets/img/logo.svg"
    
    SUCCESS_COLOR = "#31CE36"
    INFO_COLOR = "#48ABF7"
    WARNING_COLOR = "#FFAD46"
    DANGER_COLOR = "#F25961"
    
    # Configurações por Usuário
    USER_THEMES = {
        "Leandro Leal": {
            "APP_NAME": "NICE GROUP",
            "PRIMARY_COLOR": "#2E8B57",
            "SECONDARY_COLOR": "#4682B4"
        }
    }
