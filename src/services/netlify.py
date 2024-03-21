from netlify_py import NetlifyPy

from src.config import Config
from src.project import ProjectManager

class Netlify:
    def __init__(self):
        config = Config()
        api_key = config.get_netlify_api_key()
        self.netlify = NetlifyPy(access_token=api_key)

    def deploy(self, project_name: str):
        project_path = ProjectManager().get_project_path(project_name)
        
        site = self.netlify.site.create_site()
        
        print("===" * 10)
        print(site)
        
        site_id = site["id"]
        
        deploy = self.netlify.deploys.deploy_site(site_id, project_path)
        
        print("===" * 10)
        print(deploy)
        
        return deploy

