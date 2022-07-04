import {
    Chart,
    ChartSeries,
    ChartSeriesItem,
    ChartValueAxis,
    ChartValueAxisItem,
    ChartCategoryAxis,
    ChartCategoryAxisItem,
    ChartTitle,
    ChartLegend,
  } from "@progress/kendo-react-charts";
  import { COLORS } from "../constants";
  


  export const series = [

    {
      color: COLORS.total,
    },
  ];
  

  const Line = props => {

    console.log(props)
    var dates   = []
    var values   = []
    for (var i = 0, j = props.orderList.length; i < j; i++) {
        dates.push(props.orderList[i].date_of_supply);
        values.push(props.orderList[i].day_orders);
      }
    console.log(dates)
    return (
      <Chart pannable zoomable style={{ height: 350 }}>
        <ChartTitle text="Active orders" />
        <ChartLegend position="top" orientation="horizontal" />
        <ChartValueAxis>
          <ChartValueAxisItem title={{ text: "Qty per day" }} min={0} max={7} />
        </ChartValueAxis>
        <ChartCategoryAxis>
          <ChartCategoryAxisItem categories={dates} labels={{
          format: "d",
          rotation: "auto",
        }} />
        </ChartCategoryAxis>
        <ChartSeries>
          {series.map((item, idx) => (
            <ChartSeriesItem
              key={idx}
              type="line"
              tooltip={{ visible: true }}
              data={values}
              name={ "Orders"}
            />
          ))}
        </ChartSeries>
      </Chart>
    );
  };
  
  export default Line;