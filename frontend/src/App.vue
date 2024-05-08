<template>
  <div class="container">
    
  </div>
  <router-view></router-view>
</template>

<script>
export default {
  name: 'App',
  
}
</script>

<style>
html,
body {
    height: 100%;
    /* 確保html和body元素高度為瀏覽器視窗高度 */
    padding: 0px;
    margin: 0px;
    display: flex;
    /* 啟用flexbox */
    justify-content: center;
    /* 水平置中 */
    align-items: center;
    /* 垂直置中 */
}

body {
    background-color: #ffb310;
}
</style>
