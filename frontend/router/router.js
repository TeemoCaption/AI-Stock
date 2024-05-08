import { createRouter, createWebHistory } from "vue-router";
import App from "../src/App.vue";
import StockInfo from "../src/components/StockInfo.vue";

const routes = [
  {
    path: "/",
    name: "App",
    component: App,
  },
  {
    path: "/stock/:stockcode",
    name: "StockInfo",
    component: StockInfo,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
