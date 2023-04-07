import Cookies from 'js-cookie';
import create from 'zustand';

import { IAuthParams, getToken } from '@/api/common';
import { cookieKeys, queryClient } from '@/hooks/queryClient';

export const useAuth = create<{
  isLogged: boolean;
  logout(): void;
  login(data: IAuthParams): Promise<void>;
  error: boolean;
  setError(e: boolean): void;
  loading: boolean;
  setLoading(e: boolean): void;
}>((set) => ({
  isLogged: !!Cookies.get(cookieKeys.token),

  error: false,
  setError: (error) => set({ error }),

  loading: false,
  setLoading: (loading) => set({ loading }),

  logout: () => {
    Cookies.remove(cookieKeys.token);
    set({ isLogged: false });
    queryClient.clear();
  },

  login: async (data) => {
    try {
      const res = await getToken(data);
      set({ isLogged: true });
      Cookies.set(cookieKeys.token, res.access, { expires: 30 });
    } catch (e) {
      throw Error();
    }
  },
}));
