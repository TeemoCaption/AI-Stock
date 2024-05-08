<template>
    <div class="grid-container">
        <div class="info-box">
            <h3>當前股價</h3>
            <p>{{ stockInfo.CurrentPrice }}</p>
        </div>
        <div class="info-box">
            <h3>上一交易日的收盤價</h3>
            <p>{{ stockInfo.PreviousClose }}</p>
        </div>
        <div class="info-box">
            <h3>公司市值</h3>
            <p>{{ stockInfo.MarketCap }}</p>
        </div>
        <div class="info-box">
            <h3>當日成交量</h3>
            <p>{{ stockInfo.Volume }}</p>
        </div>
        <div class="info-box">
            <h3>過去52週的最高股價</h3>
            <p>{{ stockInfo.WeekHigh }}</p>
        </div>
        <div class="info-box">
            <h3>過去52週的最低股價</h3>
            <p>{{ stockInfo.WeekLow }}</p>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: "CurrentStock",
    data() {
        return {
            stockInfo: {},  // 股票資訊
            stockCode: '',  // 股票編號
        };
    },
    created() {
        // 重新從路由獲取股票編號
        this.stockCode = this.$route.params.stockcode;
    },
    mounted() {
        this.fetchStockData();
    },
    methods: {
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/getcurrent`)
                .then(response => {
                    this.stockInfo = response.data.current_data;
                    console.log(this.stockInfo);
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        }
    }
}
</script>
<style scoped>
.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);  /* 定義三個等寬的列 */
    grid-gap: 15px;  /* 設定方格之間的間隔 */
    padding: 15px; /* 容器的內邊距 */
}

.info-box {
    width: 120px;
    height: 120px;
    border: 2px solid #2c3e50;
    /* 方格的邊框 */
    border-radius: 8px;
    /* 圓角效果 */
    padding: 10px;
    /* 方格內的內邊距 */
    background-color: #f9f9f9;
    /* 背景色 */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    /* 陰影效果 */
    display: flex;
    flex-direction: column; /* 確保子元素垂直排列 */
    /* 使用 Flexbox 來垂直和水平居中文本 */
    align-items: center;
    justify-content: center;
    text-align: center;
    transition: all 0.3s ease; /* 所有屬性平滑過渡 */
    cursor: pointer;
}

.info-box:hover {
    background-color: #e2e2e2;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25); /* 增強陰影效果 */
    transform: translateY(-5px); /* 使方格向上移動，創造浮動效果 */
}

.info-box h3 {
    margin-bottom: 10px;
    margin-top: 10px;
}

.info-box p {
    margin: 0;
    /* 移除段落標籤的默認外邊距 */
}
</style>
