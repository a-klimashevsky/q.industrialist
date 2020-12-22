from typing import List

from eve.controllers import AssetsTreeController
from render_html import dump_header, dump_footer
from eve.viewmodels import AssetTreeItemViewModel


class AssetsRenderer:

    def __init__(self, cache_dir, controller: AssetsTreeController):
        self._cache_dir = cache_dir
        self._controller = controller

    def render(self):
        assets = self._controller.tree()
        glf = open('{dir}/assets_tree.html'.format(dir=self._cache_dir), "wt+", encoding='utf8')
        try:
            dump_header(glf, "Corp Assets")

            self.__dump_corp_assets_tree(glf, assets)

            dump_footer(glf)
        finally:
            glf.close()
        pass

    def __dump_corp_assets_tree(self, glf, assets: List[AssetTreeItemViewModel]):
        glf.write("""
        <!-- BEGIN: collapsable group (locations) -->
        <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
          <ul class="media-list">
            <li class="media">""")

        for view_model in assets:
            self._dump_view_model(glf, view_model)

        glf.write("""    </li>
          </ul>
        </div>
        <!-- END: collapsable group (locations) -->
        """)
        pass

    def _dump_view_model(self, glf, view_model: AssetTreeItemViewModel):
        img = '<img class="media-object icn32" src="{src}">'.format(
            src=view_model.item_icon_url)
        where = '{} '.format(view_model.location_name) if view_model.location_name else ""
        what = '<small>{}</small> '.format(view_model.item_name) if view_model.item_name else ""
        parent_id = '<a href="#id{id}"><span class="label label-primary">parent:{id}</span></a> '.format(
            id=view_model.parent_id) if view_model.parent_id else ""
        nq = ' <span class="badge">{}</span>'.format(view_model.quantity) if (view_model.quantity > 1) else ""
        iq = ' <span class="label label-info">{}</span>'.format(
            view_model.children_count) if view_model.children_count > 1 else ""
        loc_flag = ' <span class="label label-default">{}</span>'.format(
            view_model.location_type) if view_model.location_type else ""
        foreign = '<br/><span class="label label-warning">foreign</span>' if view_model.foreign else ""
        grp = '</br><span class="label label-success">{}</span>'.format(view_model.market_group) \
            if view_model.market_group else ""
        base = '</br>base: {:,.1f} ISK'.format(view_model.base_price) if not (view_model.base_price is None) else ""
        average = '</br>average: {:,.1f} ISK'.format(view_model.average_price) if view_model.average_price else ""
        adjusted = '</br>adjusted: {:,.1f} ISK'.format(view_model.adjusted_price) if view_model.adjusted_price else ""
        volume = '</br>{:,.1f} m&sup3'.format(view_model.volume) if view_model.volume else ""
        glf.write(
            '<div class="media">\n'
            ' <div class="media-left media-top">{img}</div>\n'
            ' <div class="media-body">\n'
            '  <h4 class="media-heading" id="id{id}">{where}{what}{iq}{nq}</h4>\n'
            '  {parent_id}<span class="label label-info">{id}</span>{loc_flag}{foreign}\n'
            '  {grp}{base}{average}{adjusted}{volume}\n'.
                format(
                img=img,
                where=where,
                what=what,
                parent_id=parent_id,
                id=view_model.item_id,
                nq=nq,
                iq=iq,
                loc_flag=loc_flag,
                foreign=foreign,
                grp=grp,
                base=base,
                average=average,
                adjusted=adjusted,
                volume=volume,
            )
        )
        for child in view_model.children:

            self._dump_view_model(glf, child)

        glf.write(
            ' </div>\n'
            '</div>\n'
        )
        pass
