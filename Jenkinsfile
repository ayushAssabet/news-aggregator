// Jenkins pipeline for News Aggregator: build, test, migrate, deploy, and optionally scrape

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'DEPLOY', defaultValue: true, description: 'Build and deploy services')
        booleanParam(name: 'RUN_SCRAPE', defaultValue: false, description: 'Run one-off scrape after deploy')
    }

    environment {
        REPO_URL = 'https://github.com/ayushAssabet/news-aggregator.git'
        BRANCH_NAME = 'main'
        CREDENTIALS_ID = 'news-aggregator-git-token'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        API_IMAGE = 'news-aggregator/api'
        SCRAPER_IMAGE = 'news-aggregator/scraper'
        DOCKER_BUILDKIT = '1'
        COMPOSE_DOCKER_CLI_BUILD = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Fetching code from repository'
                checkout([$class: 'GitSCM',
                    branches: [[name: "*/${BRANCH_NAME}"]],
                    userRemoteConfigs: [[url: REPO_URL, credentialsId: CREDENTIALS_ID]]
                ])
                script { currentBuild.displayName = "#${env.BUILD_NUMBER} ${BRANCH_NAME}@${env.GIT_COMMIT?.take(7)}" }
            }
        }

        stage('Build Images') {
            when { expression { return params.DEPLOY } }
            steps {
                echo 'Building API and Scraper Docker images'
                sh label: 'docker build api', script: "docker build -t ${API_IMAGE}:${env.BUILD_NUMBER} -f Dockerfile.api ."
                sh label: 'docker build scraper', script: "docker build -t ${SCRAPER_IMAGE}:${env.BUILD_NUMBER} -f Dockerfile.scraper ."
            }
        }

        stage('Test') {
            steps {
                echo 'Running unit tests inside API image'
                sh label: 'pytest', script: "docker run --rm ${API_IMAGE}:${env.BUILD_NUMBER} pytest -q"
            }
        }

        stage('Deploy Services') {
            when { expression { return params.DEPLOY } }
            steps {
                echo 'Using Jenkins-managed .env for deployment'
                withCredentials([file(credentialsId: 'env-skns', variable: 'SECRET_ENV_FILE')]) {
                    sh label: 'compose deploy', script: """
                        # Use Jenkins secret .env for compose by copying into workspace
                        cp -f "$SECRET_ENV_FILE" .env
                        docker compose -f ${DOCKER_COMPOSE_FILE} down --remove-orphans || true
                        docker compose -f ${DOCKER_COMPOSE_FILE} up -d --build
                    """
                }
            }
        }

        stage('Migrate DB') {
            when { expression { return params.DEPLOY } }
            steps {
                echo 'Applying database migrations (alembic upgrade head)'
                sh label: 'alembic upgrade', script: "docker compose -f ${DOCKER_COMPOSE_FILE} run --rm api alembic upgrade head"
            }
        }

        stage('Smoke Test') {
            steps {
                echo 'Checking API health endpoint'
                sh label: 'smoke', script: "bash -lc 'for i in {1..10}; do sleep 3; if curl -fsS http://localhost:8000/health | grep -q \"\"ok\"\"; then exit 0; fi; done; exit 1'"
            }
        }

        stage('Run One-off Scrape (optional)') {
            when { expression { return params.RUN_SCRAPE } }
            steps {
                echo 'Kicking off a one-off scraper run (limited)'
                sh label: 'scrape', script: "docker compose -f ${DOCKER_COMPOSE_FILE} run --rm scraper bash -lc 'cd scraper/news_spider && scrapy crawl news_spider -s CLOSESPIDER_ITEMCOUNT=50'"
            }
        }
    }

    post {
        success {
            echo 'News Aggregator pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Showing recent docker compose logs.'
            sh script: 'docker compose logs --tail=200 || true'
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}
