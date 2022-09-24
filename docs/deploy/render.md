### Blueprint


1. From <a href="https://dashboard.render.com" target="_blank" alt="Dashboard">Dashboard</a> Select __New__ -> __Blueprint__.


2. Check [render.yaml](https://github.com/iamrony777/javinfo-api/blob/main/render.yaml) for current Render blueprint , fork and edit if needed
    
    ```yaml
    services:
    - type: web
        name: javinfo-api
        env: docker
        region: singapore
        plan: free
        branch: dev
        healthCheckPath: /api/check
        envVars:
        - key: PLATFORM
          value: render 
        - key: CREATE_REDIS
          value: true
        - key: LOG_REQUEST
          value: false
        - key: API_USER
          sync: false
        - key: API_PASS
          sync: false
        - key: TZ
          value: UTC
    ```
    2.1. <a href="https://render.com/docs/blueprint-spec#sample-blueprint-spec" target="_blank">Sample Render Blueprint Specification</a>

2. If you have forked this repo and also connected Render with Github account then select your Fork __or__ Scroll down and paste `https://github.com/iamrony777/javinfo-api` or `https://github.com/YOUR_USERNAME/javinfo-api` in __Public Git repository__ section

    <div align="center">
      <img src="../../assets/images/render_public_git_repo.webp"></img>
    </div>

3. Only required variables to start api are `API_USER` & `API_PASS` , Set and apply

    <div align="center">
      <img src="../../assets/images/render_deploy_vars.webp"></img>
    </div>
