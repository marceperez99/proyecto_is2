const NODE_RADIUS = 10;
const MIN_SCREEN_HEIGHT = 500;
let MIN_SCREEN_WIDTH = $('.contenedor').width();
console.log(MIN_SCREEN_WIDTH)
const LINE_COLOR = '#A4A5A6';
const ARROW_COLOR = "#8c8c8c";
const ITEM_COLORS = {
    'Aprobado': '#17A2B8',
    'No Aprobado': '#6C757D',
    'Listo para su aprobación': '#007BFF',
    'En Linea Base': '#28A745',
    'En Revision': '#eeff00',
    'A modificar': '#DC3545',
    undefined: '#6C757D',
}

const divide_segment_by_ratio = (x1, y1, x2, y2, r) => ({x: (r * x2 + x1) / (1 + r), y: (r * y2 + y1) / (1 + r),});
const get_edge_arrow = (u, v, radius) => {

    const dx = u.x - v.x;
    const dy = u.y - v.y;
    let r = radius / (Math.sqrt(dx * dx + dy * dy) - radius);
    const startpoint = divide_segment_by_ratio(u.x, u.y, v.x, v.y, r);

    r = (Math.sqrt(dx * dx + dy * dy) - (radius + 7)) / (radius + 7);

    const endpoint = divide_segment_by_ratio(u.x, u.y, v.x, v.y, r);

    return {start: {...startpoint, id: u.id}, end: {...endpoint, id: v.id}}
}
const get_edges = (data, coordenadas) => {
    return data.reduce((edges, fase) =>
            [...edges,
                ...fase.items.reduce((list, u) =>
                        [
                            ...list,
                            ...u.hijos.map(v => ({start: coordenadas[u.codigo], end: coordenadas[v]})),
                            ...u.sucesores.map(v => ({start: coordenadas[u.codigo], end: coordenadas[v]}))
                        ]
                    , [])
            ]
        , []).map(edge => get_edge_arrow(edge.start, edge.end, NODE_RADIUS));
}
const topo_sort = graph => {
    let inDegree = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: 0}), {});
    let visited = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: false}), {});
    let items = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: curr}), {});

    graph.forEach(u => {
        u['hijos'].forEach(v => inDegree[v]++)
    })
    let queue = Object.keys(inDegree).filter(u => inDegree[u] === 0)
        .map(v => ({vertice: v, nivel: 0}));

    let layers = [];

    while (queue.length) {
        let u = queue.shift()
        if (!visited[u.vertice]) {
            if (u.nivel >= layers.length) layers.push([]);
            layers[u.nivel].push(u.vertice);
            items[u.vertice].hijos.forEach(v => {
                inDegree[v]--;
                if (inDegree[v] === 0) {
                    queue.push({nivel: u.nivel + 1, vertice: v})
                }
            })
        }
    }
    const span = layers.reduce((max, curr) => Math.max(max, curr.length), 0);
    return {layers, width: layers.length, span}
}
const bfs = graph => {
    let inDegree = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: 0}), {});
    let visited = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: false}), {});
    let items = graph.reduce((acc, curr) => ({...acc, [curr['codigo']]: curr}), {});

    graph.forEach(u => {
        u['hijos'].forEach(v => inDegree[v]++)
    })
    let queue = Object.keys(inDegree).filter(u => inDegree[u] === 0)
        .map(v => ({vertice: v, nivel: 0}));

    let layers = [];

    while (queue.length) {
        let u = queue.shift()
        if (!visited[u.vertice]) {
            if (u.nivel >= layers.length) layers.push([]);
            layers[u.nivel].push(u.vertice);
            items[u.vertice].hijos.forEach(v => {
                queue.push({nivel: u.nivel + 1, vertice: v})
            })
        }
    }
    const span = layers.reduce((max, curr) => Math.max(max, curr.length), 0);
    return {layers, width: layers.length, span}
}
const get_coordinates = (layering, width, height) => {
    let coordinates = {};
    let dx = width / (layering.width + 1);

    layering.layers.forEach((layer, i) => {
        let dy = height / (layer.length + 1);
        layer.forEach((node, j) => {
            coordinates[node] = {x: dx * (i + 1), y: dy * (j + 1)}
        })
    });
    return coordinates;
}

function draw_edges(svg, edges) {

    svg.selectAll(".line")
        .data(edges)
        .enter()
        .append("line")
        .attr("x1", d => d.start.x)
        .attr("y1", d => d.start.y)
        .attr("x2", d => d.end.x)
        .attr("y2", d => d.end.y)
        .attr("stroke", ARROW_COLOR)
        .attr("stroke-width", 2)
        .attr('class', d => `start-${d.start.id} end-${d.end.id}`)
        .attr("marker-end", "url(#arrow)");
}

function draw_nodes(svg, coordenadas_list, coordenadas, nodeInfo) {
    const elem = svg.selectAll("g circle")
        .data(coordenadas_list)
    const elemEnter = elem.enter()
        .append("g")


    elemEnter.append("circle")
        .attr("id", d => d.id)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("r", NODE_RADIUS)
        .attr('data-toggle', 'tooltip')
        .attr('data-html', 'true')
        .attr('data-placement', 'top')
        .attr('title', d => `<b>${nodeInfo[d.id].nombre}<br/></b>
                <span style="text-align: left;">Tipo de Item: ${nodeInfo[d.id].tipoDeItem}<br/></span>
                <span style="text-align: left;">Estado: ${nodeInfo[d.id].estado}<br/></span>
                <span style="text-align: left;">Peso: ${nodeInfo[d.id].peso}<br/></span>`)

        .on("mouseover", function (d) {
            d3.select(this).style("cursor", "move");
        })
        .on("mouseout", function (d) {
        })
        .call(
            d3.drag()
                .on('start', function (d) {
                    d3.select(this).raise().classed("active", true);
                })
                .on('drag', function (d) {
                    if (d.limits) {
                        let separator = d.limits
                        if (d3.event.x <= separator.start)
                            d.x = separator.start + NODE_RADIUS + 1;
                        else if (d3.event.x >= separator.end)
                            d.x = separator.end - NODE_RADIUS - 1;
                        else
                            d.x = d3.event.x;
                    } else {
                        d.x = d3.event.x
                    }
                    if (d3.event.y <= NODE_RADIUS) dy = NODE_RADIUS
                    else d.y = d3.event.y
                    d3.select(this).attr("cx", d.x).attr("cy", d.y);
                    coordenadas[d.id].x = d.x;
                    coordenadas[d.id].y = d.y;

                    const node_position = {x: d.x, y: d.y}
                    d3.selectAll(`.start-${d.id}`).attr('cx', function (d) {

                        const new_arrow = get_edge_arrow(node_position, coordenadas[d.end.id], NODE_RADIUS);

                        d3.select(this).attr('x1', d.start.x = new_arrow.start.x)
                            .attr('y1', d.start.y = new_arrow.start.y)
                            .attr('x2', d.end.x = new_arrow.end.x)
                            .attr('y2', d.end.y = new_arrow.end.y)
                    });
                    d3.selectAll(`.end-${d.id}`).attr('cx', function (d) {

                        const new_arrow = get_edge_arrow(coordenadas[d.start.id], node_position, NODE_RADIUS);

                        d3.select(this).attr('x1', d.start.x = new_arrow.start.x)
                            .attr('y1', d.start.y = new_arrow.start.y)
                            .attr('x2', d.end.x = new_arrow.end.x)
                            .attr('y2', d.end.y = new_arrow.end.y)
                    });
                    d3.select(`.item_id${d.id}`)
                        .attr("dx", () => node_position.x - 15)
                        .attr("dy", () => node_position.y - 15)

                })
        )
        .style("fill", function (d, i) {
                console.log(nodeInfo[d.id].estado)
                return ITEM_COLORS[nodeInfo[d.id].estado];
            }
        )
    elemEnter.append("text")
        .attr("class", d => `item_id${d.id}`)
        .attr("dx", function (d) {
            return d.x - 15
        })
        .attr("dy", function (d) {
            return d.y - 15
        })
        .text(function (d) {
            return d.id
        })

}

function draw_divisorias(svg, data, height, width) {

    svg.selectAll('line')
        .data(data)
        .enter()
        .append("line")
        .style("stroke", LINE_COLOR)
        .attr("x1", d => d)
        .attr("y1", 0)
        .attr("x2", d => d)
        .attr("y2", height);

    svg.append('line')
        .style("stroke", LINE_COLOR)
        .attr("x1", 0)
        .attr("y1", 20)
        .attr("x2", width)
        .attr("y2", 20);
}

function draw_titulos_fases(svg, data) {
    svg.selectAll('.titles')     // declare a new CSS class 'dummyText'
        .data(data)
        .enter()                     // create new element
        .append("text")              // add element to class
        .attr("font-family", "sans-serif")
        .attr("font-size", "14px")
        .attr("dx", d => d.x)
        .style("text-anchor", "middle")
        .attr("dy", '15px')
        //.attr("opacity", 0.0)      // not really necessary
        .text(function (d) {
            return d.title
        })
}

function graficar_DAG(data, algorithm) {
    console.log(data)
    let fases = data.map(fase => fase.fase)
    let itemInfo = {}
    data.forEach(fase => fase.items.forEach(item => itemInfo[item.codigo] = {...item.data}))

    const layering = data.map(fase => algorithm(fase.items));
    let x_offset = 0;
    let divisorias = [];
    let coordenadas = {};
    let span = layering.reduce((max, curr) => Math.max(max, curr.span), 0)
    let height = Math.max(5 * NODE_RADIUS * (2 * span + 1), MIN_SCREEN_HEIGHT);
    let fasesNamesLength = get_text_length(fases)
    let tituloFaseCoordenadas = [];
    layering.forEach((layer, i) => {
        const width = Math.max(2 * NODE_RADIUS * (2 * layer.width + 1), fasesNamesLength[i] + 10, MIN_SCREEN_WIDTH / layering.length);

        const layer_coordinates = Object.entries(get_coordinates(layer, width, height - 2))
            .map(e => {
                e[1].y += 20;
                return e
            })
            .reduce((acc, [item, pos]) => {

                return {
                    ...acc, [item]: {
                        id: item,
                        x: pos.x + x_offset,
                        y: pos.y,
                        limits:
                            {
                                start: x_offset,
                                end: x_offset + width
                            }
                    }
                }
            }, {});
        tituloFaseCoordenadas.push(x_offset + width / 2);
        x_offset += width;
        divisorias.push(x_offset);

        coordenadas = {...coordenadas, ...layer_coordinates};
    });
    let width = x_offset;
    fases = fases.map((fase, i) => ({x: tituloFaseCoordenadas[i], title: fase}));

    const svg = d3.select("svg")
        .style('width', MIN_SCREEN_WIDTH)
        .style('height', MIN_SCREEN_HEIGHT)
        .style('border', `1px solid ${LINE_COLOR}`)
        .style('border-radius', `5px`)
        .call(d3.zoom().on("zoom", () => {
            svg.attr("transform", d3.event.transform)
        })).call(d3.zoom().on("zoom", () => {
            svg.attr("transform", d3.event.transform)
        }).scaleExtent([
            Math.min(1, MIN_SCREEN_HEIGHT * MIN_SCREEN_WIDTH / (width * height))
            , 2]).translateExtent([[0, 0], [width, height]]))
        .append("g");

    let coordenadas_list = Object.entries(coordenadas).map(([item, pos]) => ({
        id: item,

        x: pos.x,
        y: pos.y,
        limits: pos.limits
    }));

    const edges = get_edges(data, coordenadas);
    divisorias.pop()
    console.log(divisorias)
    draw_divisorias(svg, divisorias, height, width);
    draw_titulos_fases(svg, fases)
    draw_edges(svg, edges);
    draw_nodes(svg, coordenadas_list, coordenadas, itemInfo);


    return layering
}

function get_text_length(fases) {
    let textWidth = []

    d3.select('body')
        .append("svg")
        .selectAll('.dummyText')     // declare a new CSS class 'dummyText'
        .data(fases)
        .enter()                     // create new element
        .append("text")              // add element to class
        .attr("font-family", "sans-serif")
        .attr("font-size", "14px")
        //.attr("opacity", 0.0)      // not really necessary
        .text(function (d) {
            return d
        })
        .each(function (d, i) {
            const thisWidth = this.getComputedTextLength()
            textWidth.push(thisWidth)
            this.remove() // remove them just after displaying them
        }).remove()
    return textWidth;
}


let graficado = false;

$('#trazabilidad-tab').on('shown.bs.tab', function () {
    if (!graficado) {
        MIN_SCREEN_WIDTH = $('.contenedor').width();
        graficar_DAG(graph, topo_sort);
        graficado = true;
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })
    }
});
$('#visualizacion1').click(function () {
    $(this).addClass('active');
    $('#visualizacion2').removeClass('active');
    d3.select("svg g").remove();
    graficar_DAG(graph, topo_sort);
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
})
$('#visualizacion2').click(function () {
    $(this).addClass('active');
    $('#visualizacion1').removeClass('active');
    d3.select("svg g").remove();
    graficar_DAG(graph, bfs);
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
})