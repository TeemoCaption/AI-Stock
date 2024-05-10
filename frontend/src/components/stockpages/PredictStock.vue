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
        const today = new Date();
        const tenDaysAgo = new Date(today.setDate(today.getDate() - 10)).toISOString().slice(0, 10);
        const endDate = new Date().toISOString().slice(0, 10);

        return {
            startDate: tenDaysAgo,
            endDate: endDate,
            stockData: [],
            stockCode: '',  // 股票編號
        };
    },
    created() {
        // 重新從路由獲取股票編號
        this.stockCode = this.$route.params.stockcode;
    },
    mounted() {
        this.fetchStockData();
        this.drawChart();
    },
    methods: {
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/gethistory`, {
                params: {
                    start_date: this.startDate,
                    end_date: this.endDate
                }
            })
                .then(response => {
                    const fullData = response.data.historical_data;
                    this.stockData = fullData.map(item => {
                        const dateObj = new Date(item.date);
                        const year = dateObj.getFullYear();
                        const month = dateObj.getMonth() + 1;  // getMonth 返回的月份從 0 開始
                        const date = dateObj.getDate();
                        const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${date.toString().padStart(2, '0')}`;  // 將月份和日期格式化為兩位數

                        return {
                            date: formattedDate,
                            close: Math.round(parseFloat(item.close) * 100) / 100,  // 四捨五入到小數點後兩位
                            volume: parseInt(item.volume || 0)  // 如果 volume 存在則解析，否則設為0
                        };
                    });
                    this.$nextTick(() => {
                        setTimeout(() => {
                            this.updateChart(this.$refs.chart);
                        }, 500);  // 延遲1秒後再更新圖表
                    });
                    console.log(this.stockData);
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        },
        drawChart() {
            const container = this.$refs.chart;
            const resizeObserver = new ResizeObserver(() => {
                this.updateChart(container);
            });
            resizeObserver.observe(container);
        },

        updateChart(container) {
            if (!container || this.stockData.length === 0) return;
            d3.select(container).select('svg').remove();

            const width = container.clientWidth || 600; // 為避免寬度為0，提供默認最小寬度
            const height = container.clientHeight;

            const svg = d3.select(container)
                .append('svg')
                .attr('width', '100%') // 使用百分比以適應容器
                .attr('height', '100%') // 使用百分比以適應容器
                .style('background-color', 'white');

            const margin = { top: 20, right: 70, bottom: 60, left: 40 };
            const drawingWidth = width - margin.left - margin.right;
            const drawingHeight = height - margin.top - margin.bottom;

            const g = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

            const parseDate = d3.timeParse('%Y-%m-%d');

            this.stockData.forEach(d => {
                d.date = parseDate(d.date);
                d.close = +d.close;
                d.volume = +d.volume;
            });

            const x = d3.scaleTime()
                .domain([d3.min(this.stockData, d => d.date), d3.max(this.stockData, d => d.date)])
                .range([0, drawingWidth]);

            const yPrice = d3.scaleLinear()
                .domain([0, d3.max(this.stockData, d => d.close)])
                .range([drawingHeight, 0]);

            const yVolume = d3.scaleLinear()
                .domain([0, d3.max(this.stockData, d => d.volume)])
                .range([drawingHeight, 0]);

            const barWidth = this.stockData.length > 0 ? Math.max(1, Math.min(20, drawingWidth / this.stockData.length)) : 0;


            const line = d3.line()
                .x(d => x(d.date))
                .y(d => yPrice(d.close));

            g.append('path')
                .datum(this.stockData)
                .attr('fill', 'none')
                .attr('stroke', '#be0027')
                .attr('stroke-width', 2)
                .attr('d', line);

            g.selectAll('.bar')
                .data(this.stockData)
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('x', d => x(d.date) - barWidth / 2)
                .attr('y', d => yVolume(d.volume))
                .attr('width', barWidth)
                .attr('height', d => drawingHeight - yVolume(d.volume))
                .attr('fill', '#11862f');

            const totalDays = d3.timeDay.count(d3.min(this.stockData, d => d.date), d3.max(this.stockData, d => d.date)) + 1;
            const tickInterval = totalDays > 30 ? 7 : 1; // 如果總天數超過30天，則每七天顯示一次日期，否則每天都顯示

            let lastYear = null;
            let lastMonth = null;
            g.append('g')
                .attr('transform', `translate(0, ${drawingHeight})`)
                .call(d3.axisBottom(x).ticks(d3.timeDay.every(tickInterval)).tickFormat(date => {
                    const year = date.getFullYear();
                    const month = date.getMonth();
                    if (lastYear !== year) {
                        lastYear = year;
                        lastMonth = month;
                        return d3.timeFormat('%Y')(date);
                    } else if (lastMonth !== month) {
                        lastMonth = month;
                        return d3.timeFormat('%m-%d')(date);
                    } else if (this.stockData.length <= 30) { // 如果資料點少於或等於30，則顯示日
                        return d3.timeFormat('%m-%d')(date);
                    } else {
                        return '';
                    }
                }));


            g.append('g')
                .call(d3.axisLeft(yPrice));

            g.append('g')
                .attr('transform', `translate(${drawingWidth}, 0)`)
                .call(d3.axisRight(yVolume));
        }
    }
}
</script>

<style scoped>
.history-chart {
    width: 100%;
    height: 400px;
    margin-top: 15px;
    border: 2px solid #11862f;
}
</style>