<template>
  <div>
    <h1>股票編號： {{ stockCode }}</h1>
    <nav>
      <router-link :to="{ name: 'CurrentStock', params: { stockcode: stockCode } }">今日股票資訊</router-link>
      <router-link :to="{ name: 'HistoryStock', params: { stockcode: stockCode } }">過去股票資訊</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'StockInfo',
  data() {
    return {
      stockCode: ''
    }
  },
  created() {
    this.stockCode = this.$route.params.stockcode;
  }
}
</script>

<style scoped>
*{
  /*border: solid 1px; */
}

div {
  display: flex;
  flex-direction: column; /* 垂直排列子元素 */
  align-items: center; /* 水平置中 */
  justify-content: center; /* 垂直居中 */
  /*height: 100vh; /* 讓 div 占滿整個視窗高度 */
  padding: 10px; /* 較小的內邊距 */
}

h1{
  margin-bottom: 20px; /* 調整標題與下方元素間的間距 */
}

nav {
  padding: 15px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  padding: 10px;
  border-radius: 4px;
  margin-right: 5px; /* 添加適當的右邊距 */
}

nav a.router-link-exact-active {
  color: white;
  background: #11862f;
}
</style>
