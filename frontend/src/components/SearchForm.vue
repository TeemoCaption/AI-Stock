<template>
    <div v-if="showSearch" class="search-section">
        <h1>股票分析助手</h1>
        <p>※股票資訊來自奇摩股市</p>
        <!-- @submit.prevent：阻止表單默認跳轉行為 -->
        <form class="search" @submit.prevent="handleSubmit">
            <div class="search-bar">
                <!-- v-model 會根據輸入框的值動態更新 stockCode變數值 -->
                <input type="text" v-model="stockCode" class="search-input" placeholder="輸入股票代號...">
                <button class="search-button" type="submit">搜尋</button>
            </div>
        </form>
    </div>
</template>

<script>
export default {
    name: 'SearchForm',
    data() {
        return {
            stockCode: '',
            showSearch: true,
            errorMessage: ''  // 新增一個用於儲存錯誤消息的變數
        };
    },
    methods: {
        handleSubmit() {
            if (this.stockCode.trim() === '') {
                this.errorMessage = '請輸入股票代號。'; // 更新錯誤消息
                return; // 如果股票代號為空，則不執行後續的路由跳轉
            }
            this.$router.push({ name: 'CurrentStock', params: { stockcode: this.stockCode } });
            this.showSearch = false; // 在跳轉後隱藏搜索表單
            this.errorMessage = ''; // 清空任何存在的錯誤消息
        }
    },
    watch: {
        $route(to) {
            // 當路由變化回到根路徑時顯示搜索表單
            this.showSearch = to.path === '/';
        }
    }
}
</script>

<style>
.search-section {
    display: flex;
    /* 啟用 flexbox */
    flex-direction: column;
    /* 指定 flex 方向為垂直 */
    justify-content: center;
    /* 垂直置中 */
    align-items: center;
    /* 水平置中 */
    height: 100vh;
    /* 設定高度為視窗的100%，確保有足夠空間垂直置中 */
    text-align: center;
}

.search-section h1 {
    margin-top: 20px;
    /* 上邊距 */
    margin-bottom: 10px;
    /* 下邊距 */
}

.search-section p {
    margin-top: 0;
    margin-bottom: 20px;
}

.search-bar {
    display: flex;
    border: 2px solid #11862f;
    border-radius: 5px;
    overflow: hidden;
}

.search-input {
    padding: 10px;
    border: none;
    outline: none;
    font-size: 16px;
    width: 300px;
}

.search-button {
    padding: 10px 20px;
    background-color: #11862f;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 16px;
}

.search-button:hover {
    background-color: #01cd74;
}
</style>