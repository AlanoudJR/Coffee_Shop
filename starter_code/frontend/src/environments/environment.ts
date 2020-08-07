/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'test-alanoud.us.auth0.com', // the auth0 domain prefix
    audience: 'drinks', // the audience set for the auth0 app
    clientId: '3Hd4Of7KRQq5biFW1y3glQ8A5WhZ4Rn2', // the client id generated for the auth0 app
    callbackURL: 'https://127.0.0.1:8080/login-results'//'http://localhost:8100', // the base url of the running ionic application. 
    //Check the callbackURL
  }
};
