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
        window.addEventListener('resize', this.updateDimensions);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.updateDimensions);
    },
    methods: {
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/getpredict5`, {})
                .then(response => {
                    const predictData = response.data.predict_data;
                    let currentDate = new Date();
                    currentDate.setDate(currentDate.getDate() + 1); // 從明天開始
                    for (let i = 0; i < Math.min(predictData.length, 5); i++) {
                        this.stockData.push({
                            date: new Date(currentDate.toISOString().slice(0, 10)), // 轉換為日期對象
                            close: +predictData[i], // 轉換為數字
                        });
                        currentDate.setDate(currentDate.getDate() + 1);
                    }
                    this.drawChart(); // 在數據加載完後呼叫
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        },
        updateDimensions() {
            d3.select(this.$refs.chart).select('svg').remove(); // 移除舊的SVG元素
            this.drawChart(); // 重新繪製圖表
        },
        drawChart() {
            const container = this.$refs.chart;
            const svg = d3.select(container)
                .append('svg')
                .style('min-width', '500px')  // 設置最小寬度為500px
                .attr('width', '100%')
                .attr('height', '100%')
                .style('background-color', 'white');  // 設置SVG背景色為白色

            const margin = { top: 20, right: 20, bottom: 30, left: 50 };
            const width = svg.node().getBoundingClientRect().width - margin.left - margin.right;
            const height = svg.node().getBoundingClientRect().height - margin.top - margin.bottom;

            const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

            // 在 drawChart 方法中
            const x = d3.scaleTime().rangeRound([0, width]);
            const y = d3.scaleLinear().rangeRound([height, 0]);

            const line = d3.line()
                .x(d => x(d.date))
                .y(d => y(d.close));

            let startDate = this.stockData[0].date;  // 起始日期為資料的第一天
            let endDate = new Date(startDate.getTime());
            endDate.setDate(endDate.getDate() + 4);  // 結束日期為起始日期後的第五天
            x.domain([startDate, endDate]);  // 將 x 的範圍設定為這五天

            y.domain(d3.extent(this.stockData, d => d.close));

            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%m/%d")));  // 修改此行


            g.append('g')
                .call(d3.axisLeft(y))
                .append('text')
                .attr('fill', '#000')
                .attr('transform', 'rotate(-90)')
                .attr('y', 6)
                .attr('dy', '0.71em')
                .attr('text-anchor', 'end')
                .text('Close Price ($)');

            g.append('path')
                .datum(this.stockData)
                .attr('fill', 'none')
                .attr('stroke', 'red')  // 將線段顏色設為紅色
                .attr('stroke-linejoin', 'round')
                .attr('stroke-linecap', 'round')
                .attr('stroke-width', 1.5)
                .attr('d', line);

            // 添加紅色資料點
            g.selectAll('dot')
                .data(this.stockData)
                .enter().append('circle')
                .attr('r', 5)
                .attr('cx', d => x(d.date))
                .attr('cy', d => y(d.close))
                .style('fill', 'red');  // 資料點填充為紅色
        }
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