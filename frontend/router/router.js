import { createRouter, createWebHistory } from "vue-router";
import SearchForm from "../src/components/SearchForm.vue";
import StockInfo from "../src/components/StockInfo.vue";

const routes = [
  {
    path: "/",
    name: "SearchForm",
    component: SearchForm,
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
