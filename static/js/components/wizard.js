 Vue.component('pager', {
    delimiters: ['[[', ']]'],
    props: ['page', 'max'],
    template: '<div class="text-white">[[ page ]]/[[ max ]]</div>'
})

Vue.component('project-select', {
    delimiters: ['[[', ']]'],
    props: [],
    template: `
    <div>
        <div>or select</div>
    
        <div v-if="projects.length > 0" class="dropdown">
            <button class="btn btn-projects dropdown-toggle" type="button" id="wizard-projects-dropdown"
                data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Select project
            </button>
            <div class="dropdown-menu" aria-labelledby="wizard-projects-dropdown">
                <a v-for="p in projects" :key="p.id" @click="selectProject(p)" class="dropdown-item" href="#">[[ p.name ]]</a>
            </div>
        </div>
    </div>
    `,
    data() {
        return {
            projects: [],
        }
    },
    async mounted() {
        console.log('create pr mounted');
        const data = await fetch('/api/v1/project?offset=0', {
            headers: {'content-type': 'application/json'}
        })
        this.projects = await data.json()
        console.log('fetched data', this.projects)
    },
    methods: {

        selectProject(project) {
            console.log('SElected project', project.name, project.id)
            fetch(`api/v1/project-session/${project.id}`, {
                method: 'POST',
                headers: {'content-type': 'application/json'},
                body: JSON.stringify({username: null, groups: null})
            }).then(response => response.ok && location.replace('/'))

        }
    }
})

Vue.component('page2-slider', {
    delimiters: ['[[', ']]'],
    props: [],
    template: `
<div class="card" style="max-height: 590px;">
    <div class="card-header" style="max-height: 70px">
        <div class="row">
            <div class="col-4"><h3>Virtual users hours</h3><div>[[ vuh ]]</div></div>
            <div class="col"><h3>Estimated monthly cost</h3><div>[[ cost ]]</div></div>
        </div>
    </div>
    
    <div class="card-body">
        <div class="card" style="height: 60px">
            <div ref="slider"></div>
        </div>
        <div class="card-table">
            <table class="table table-borderless" ref="activitiesTable">
                <thead class="thead-light">
                    <tr>
                        <th scope="col" data-sortable="true" data-cell-style="nameStyle" data-field="activity">Activity</th>
                        <th scope="col" data-sortable="true" data-cell-style="nameStyle" data-field="description">Description</th>
                        <th scope="col" data-sortable="true" data-cell-style="nameStyle" data-field="vuh_cost">Vuh cost</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
    </div>
    
</div>


`,
    data() {
        return {
            vuh: 0,
            columns: [1,2,3,4,5],
            // data: []
        }
    },
    mounted() {
        noUiSlider.create(this.$refs.slider, {
            start: 500,
            range: {
                'min': 500,
                'max': 60000
            },
            step: 500,
            format: wNumb({
                decimals: 0
            }),
            pips: {
                mode: 'values',
                values: [500, 5000, 20000, 40000, 60000],
                density: 3
            }
        })

        const vm = this;
        this.$refs.slider.noUiSlider.on('update', function (values, handle, unencoded, isTap, positions) {
            vm.vuh = parseInt(values[handle])
            vm.$emit("input", vm.vuh)
        })

        $(this.$refs.activitiesTable).bootstrapTable({
              data: vm.activities
            })
    },
    computed: {
        cost() {
            return this.vuh === 500 ? "FREE" : `${this.vuh * 0.1} $`
        },
        activities() {
            const data = []
            let i;
            for (i = 1; i<8; i++) {
                data.push(this.createActivity(i))
            }
            return data;
        }
    },
    methods: {
        createActivity(num) {
            return {activity: `Activity ${num}`, description: 'Lorem Ipsum', vuh_cost: Math.random() * 10000}
        }
    }
})


const wizardApp = new Vue({
        delimiters: ['[[', ']]'],
        el: '#wizard-container',
        data() {
            return {
                page: 2,
                maxPages: 5,
                projectName: '',
                vuh: 0
            }
        },
        mounted() {
            console.log('wizardApp mounted')
        },
        computed: {},
        methods: {
        }

    })
;
