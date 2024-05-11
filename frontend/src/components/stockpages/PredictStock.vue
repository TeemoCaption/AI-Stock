<template>
    <div>
        <div class="predict-chart" ref="chart"></div>
    </div>
</template>

<script>
import * as d3 from 'd3';
import axios from 'axios';

export default {
    name: 'PredictStock',
    data() {
        return {
            stockData: [],
            stockCode: '',
        };
    },
    created() {
        this.stockCode = this.$route.params.stockcode;
    },
    mounted() {
        this.fetchStockData();
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.updateDimensions);
    },
    methods: {
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/getpredict`, {})
                .then(response => {
                    const predictData = response.data.predict_data;
                    let currentDate = new Date();
                    currentDate.setDate(currentDate.getDate() + 1); // 從明天開始
                    for (let i = 0; i < Math.min(predictData.length, 5); i++) {
                        this.stockData.push({
                            date: currentDate.toISOString().slice(0, 10),
                            close: predictData[i],
                        });
                        currentDate.setDate(currentDate.getDate() + 1);
                    }
                    this.drawChart(); // 在數據加載完後呼叫
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        },
        
    }
}
</script>

<style scoped>
.predict-chart {
    width: 100%;
    height: 400px;
    margin-top: 15px;
    border: 2px solid #11862f;
}

</style>