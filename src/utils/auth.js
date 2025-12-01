import { PublicClientApplication } from '@azure/msal-browser';

// MSAL 配置
export const msalConfig = {
  auth: {
    clientId: 'YOUR_CLIENT_ID',
    authority: 'https://login.microsoftonline.com/YOUR_TENANT_ID',
    redirectUri: window.location.origin + '/dashboard',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  }
};

// 登入請求配置
export const loginRequest = {
  scopes: ['User.Read', 'api://YOUR_API_CLIENT_ID/access_as_user'] // 加入你的 API 權限
};

// Token 請求配置
export const tokenRequest = {
  scopes: ['api://YOUR_API_CLIENT_ID/access_as_user'], // API 訪問權限
};

// 初始化 MSAL 實例（單例模式）
let msalInstance = null;

export const getMsalInstance = async () => {
  if (!msalInstance) {
    msalInstance = new PublicClientApplication(msalConfig);
    await msalInstance.initialize();
  }
  return msalInstance;
};

// 取得 Access Token
export const getAccessToken = async () => {
  try {
    const instance = await getMsalInstance();
    const accounts = instance.getAllAccounts();

    if (accounts.length === 0) {
      console.error('No accounts found');
      return null;
    }

    // 嘗試靜默取得 Token
    try {
      const response = await instance.acquireTokenSilent({
        ...tokenRequest,
        account: accounts[0]
      });
      return response.accessToken;
    } catch (error) {
      // 如果靜默取得失敗，使用 Popup
      if (error.name === 'InteractionRequiredAuthError') {
        const response = await instance.acquireTokenPopup(tokenRequest);
        return response.accessToken;
      }
      throw error;
    }
  } catch (error) {
    console.error('Error getting access token:', error);
    return null;
  }
};

// 取得 ID Token (JWT)
export const getIdToken = async () => {
  try {
    const instance = await getMsalInstance();
    const accounts = instance.getAllAccounts();

    if (accounts.length === 0) {
      return null;
    }

    const response = await instance.acquireTokenSilent({
      ...loginRequest,
      account: accounts[0]
    });
    
    return response.idToken;
  } catch (error) {
    console.error('Error getting ID token:', error);
    return null;
  }
};

// 取得使用者資訊
export const getUserInfo = async () => {
  try {
    const instance = await getMsalInstance();
    const accounts = instance.getAllAccounts();
    
    if (accounts.length > 0) {
      return {
        name: accounts[0].name,
        email: accounts[0].username,
        id: accounts[0].localAccountId
      };
    }
    return null;
  } catch (error) {
    console.error('Error getting user info:', error);
    return null;
  }
};

// 檢查是否已登入
export const isAuthenticated = async () => {
  try {
    const instance = await getMsalInstance();
    const accounts = instance.getAllAccounts();
    return accounts.length > 0;
  } catch (error) {
    return false;
  }
};

// 登出
export const logout = async () => {
  try {
    const instance = await getMsalInstance();
    await instance.logoutPopup();
    sessionStorage.clear();
  } catch (error) {
    console.error('Logout error:', error);
  }
};