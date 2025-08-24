# 海しるAPIの実行方法（1件のデータの確認方法）
## 島名
```
https://api.msil.go.jp/island/v2/MapServer/1/query
 ?where=1=1
 &outFields=*
 &returnGeometry=true
 &resultRecordCount=1
 &f=json
 &subscription-key=0e83ad5d93214e04abf37c970c32b641
```
```
{
  "displayFieldName": "島名",
  "fieldAliases": {
    "島名": "島名",
    "読み": "読み",
    "都道府県": "都道府県",
    "管区": "管区",
    "出典_情報提供者": "出典・情報提供者"
  },
  "geometryType": "esriGeometryPoint",
  "spatialReference": {
    "wkid": 4326,
    "latestWkid": 4326
  },
  "fields": [
    {
      "name": "島名",
      "type": "esriFieldTypeString",
      "alias": "島名",
      "length": 30
    },
    {
      "name": "読み",
      "type": "esriFieldTypeString",
      "alias": "読み",
      "length": 30
    },
    {
      "name": "都道府県",
      "type": "esriFieldTypeString",
      "alias": "都道府県",
      "length": 10
    },
    {
      "name": "管区",
      "type": "esriFieldTypeString",
      "alias": "管区",
      "length": 255
    },
    {
      "name": "出典_情報提供者",
      "type": "esriFieldTypeString",
      "alias": "出典・情報提供者",
      "length": 255
    }
  ],
  "features": [
    {
      "attributes": {
        "島名": "弁天島",
        "読み": "Benten Shima",
        "都道府県": "北海道",
        "管区": "第一管区海上保安本部",
        "出典_情報提供者": "海上保安庁"
      },
      "geometry": {
        "x": 145.5763058,
        "y": 43.3420288
      }
    }
  ],
  "exceededTransferLimit": true
}
```
## 海底地形名
```
https://api.msil.go.jp/undersea-features/v2/MapServer/1/query
 ?where=1=1
 &outFields=*
 &returnGeometry=true
 &resultRecordCount=1
 &f=json
 &subscription-key=0e83ad5d93214e04abf37c970c32b641
```
```
{
  "displayFieldName": "海底地形名",
  "fieldAliases": {
    "海底地形名": "海底地形名",
    "かな": "かな",
    "Undersea_Feature_Name": "Undersea_Feature_Name",
    "属名": "属名",
    "水深": "水深",
    "呼称の由来": "呼称の由来",
    "由来_En": "由来_En",
    "会議名": "会議名",
    "JCUFN_approved": "JCUFN_approved",
    "SCUFN_approved": "SCUFN_approved"
  },
  "geometryType": "esriGeometryPoint",
  "spatialReference": {
    "wkid": 4326,
    "latestWkid": 4326
  },
  "fields": [
    {
      "name": "海底地形名",
      "type": "esriFieldTypeString",
      "alias": "海底地形名",
      "length": 255
    },
    {
      "name": "かな",
      "type": "esriFieldTypeString",
      "alias": "かな",
      "length": 50
    },
    {
      "name": "Undersea_Feature_Name",
      "type": "esriFieldTypeString",
      "alias": "Undersea_Feature_Name",
      "length": 255
    },
    {
      "name": "属名",
      "type": "esriFieldTypeString",
      "alias": "属名",
      "length": 255
    },
    {
      "name": "水深",
      "type": "esriFieldTypeSmallInteger",
      "alias": "水深"
    },
    {
      "name": "呼称の由来",
      "type": "esriFieldTypeString",
      "alias": "呼称の由来",
      "length": 255
    },
    {
      "name": "由来_En",
      "type": "esriFieldTypeString",
      "alias": "由来_En",
      "length": 200
    },
    {
      "name": "会議名",
      "type": "esriFieldTypeString",
      "alias": "会議名",
      "length": 255
    },
    {
      "name": "JCUFN_approved",
      "type": "esriFieldTypeSmallInteger",
      "alias": "JCUFN_approved"
    },
    {
      "name": "SCUFN_approved",
      "type": "esriFieldTypeSmallInteger",
      "alias": "SCUFN_approved"
    }
  ],
  "features": [
    {
      "attributes": {
        "海底地形名": "東崎堆",
        "かな": "あがりざきたい",
        "Undersea_Feature_Name": "Agarizaki Bank",
        "属名": "堆",
        "水深": 66,
        "呼称の由来": "近傍地名に由来（与那国島東崎）",
        "由来_En": "Named from the nearby feature/s.",
        "会議名": "第12回海洋地名打合せ会 (1981)",
        "JCUFN_approved": 1981,
        "SCUFN_approved": null
      },
      "geometry": {
        "x": 123.108333333,
        "y": 24.47
      }
    }
  ],
  "exceededTransferLimit": true
}
```