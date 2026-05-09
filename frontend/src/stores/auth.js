import { defineStore } from "pinia";
import { authApi } from "../api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    user: JSON.parse(localStorage.getItem("user") || "null"),
  }),
  actions: {
    async login(data) {
      const res = await authApi.login(data);
      this.setAuth(res);
    },
    async register(data) {
      const res = await authApi.register(data);
      this.setAuth(res);
    },
    setAuth(res) {
      this.token = res.access_token;
      this.user = res.user;
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
    },
    logout() {
      this.token = "";
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
});
