create user keycloak_user with password 'keycloak_password';
create database keycloak;
grant all privileges on database keycloak to keycloak_user;
grant all on schema public to keycloak_user;
