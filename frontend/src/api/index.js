import http from "./http";

export const authApi = {
  login: (data) => http.post("/auth/login", data),
  register: (data) => http.post("/auth/register", data),
  me: () => http.get("/auth/me"),
};

export const novelApi = {
  list: () => http.get("/novels"),
  create: (data) => http.post("/novels", data),
  update: (id, data) => http.put(`/novels/${id}`, data),
  remove: (id) => http.delete(`/novels/${id}`),
};

export const aiApi = {
  idea: (data) => http.post("/ai/idea", data),
  characters: (data) => http.post("/ai/characters", data),
  world: (data) => http.post("/ai/world", data),
  outlines: (data) => http.post("/ai/outlines", data),
  chapter: (data) => http.post("/ai/chapter", data),
  revise: (id, mode, data) => {
    const map = { 续写: "continue", 润色: "polish", 改写: "rewrite" };
    return http.post(`/ai/chapters/${id}/${map[mode] || mode}`, data);
  },
  records: () => http.get("/ai-records"),
};

export const characterApi = {
  list: (novelId) => http.get(`/novels/${novelId}/characters`),
  create: (novelId, data) => http.post(`/novels/${novelId}/characters`, data),
  update: (id, data) => http.put(`/characters/${id}`, data),
  remove: (id) => http.delete(`/characters/${id}`),
};

export const worldApi = {
  list: (novelId) => http.get(`/novels/${novelId}/world-settings`),
  create: (novelId, data) =>
    http.post(`/novels/${novelId}/world-settings`, data),
  update: (id, data) => http.put(`/world-settings/${id}`, data),
  remove: (id) => http.delete(`/world-settings/${id}`),
};

export const outlineApi = {
  list: (novelId) => http.get(`/novels/${novelId}/outlines`),
  create: (novelId, data) => http.post(`/novels/${novelId}/outlines`, data),
  batch: (novelId, data) =>
    http.post(`/novels/${novelId}/outlines/batch`, data),
  update: (id, data) => http.put(`/outlines/${id}`, data),
  remove: (id) => http.delete(`/outlines/${id}`),
};

export const chapterApi = {
  list: (novelId) => http.get(`/novels/${novelId}/chapters`),
  create: (novelId, data) => http.post(`/novels/${novelId}/chapters`, data),
  update: (id, data) => http.put(`/chapters/${id}`, data),
  remove: (id) => http.delete(`/chapters/${id}`),
};

export const submissionApi = {
  preview: (novelId) => http.get(`/novels/${novelId}/submission-preview`),
  list: () => http.get("/submissions"),
  create: (data) => http.post("/submissions", data),
  update: (id, data) => http.put(`/submissions/${id}`, data),
  remove: (id) => http.delete(`/submissions/${id}`),
};

export const dashboardApi = {
  dashboard: () => http.get("/dashboard"),
  stats: () => http.get("/stats"),
};

export const knowledgeApi = {
  list: (novelId) => http.get(`/novels/${novelId}/knowledge-items`),
  create: (novelId, data) =>
    http.post(`/novels/${novelId}/knowledge-items`, data),
  update: (id, data) => http.put(`/knowledge-items/${id}`, data),
  remove: (id) => http.delete(`/knowledge-items/${id}`),
};

export const promptApi = {
  list: () => http.get("/prompt-templates"),
  create: (data) => http.post("/prompt-templates", data),
  update: (id, data) => http.put(`/prompt-templates/${id}`, data),
};
