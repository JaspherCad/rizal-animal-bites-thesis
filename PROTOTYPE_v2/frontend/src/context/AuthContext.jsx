import { createContext, useContext, useState } from "react";

//HOW TO FUCKING READ?

//FIRST, imagine the react main part we have AuthProvider (not context  )

//   <React.StrictMode>
//     <AuthProvider>
//       <BrowserRouter>
//         <App />
//       </BrowserRouter>
//     </AuthProvider>
//   </React.StrictMode>



//2L read the "AUTHPROVIDER where it uses AuthContext" where it returns context

//3: const AuthContext = createContext(null);



const AuthContext = createContext(null);









export function AuthProvider({ children }) {
  // later this can come from Supabase session
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = () => setIsAuthenticated(true);
  const logout = () => setIsAuthenticated(false);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
