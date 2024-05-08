import { createRouter, createWebHashHistory } from "vue-router";
import SearchForm from "../src/components/SearchForm.vue";
import StockInfo from "../src/components/StockInfo.vue";
import CurrentStock from "../src/components/stockpages/CurrentStock.vue";
import HistoryStock from "../src/components/stockpages/HistoryStock.vue";

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
    children: [
      {
        path: "currentStock",
        name: "CurrentStock",
        component: CurrentStock
      },
      {
        path: "historyStock",
        name: "HistoryStock",
        component: HistoryStock
      },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
