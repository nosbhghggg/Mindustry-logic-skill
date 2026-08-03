## Translation Contribution
(v8 are currently in progress, its better to not translate this yet as the english structure might change)

1. Create a new YAML file in the `Languages/v7/` or `Languages/v8/` directory named after the language code (e.g., `fr.yaml` for French)
2. Copy the structure from the English translation file (`en.yaml`)
3. Update `index.yaml` to include an entry with:
    - `lang_code`: the file name without extension
    - `language`: the display name of the language
4. Translate the YAML values only.

Example entry in `index.json`:
```json
{ "language": "Français", "lang_code": "fr"}
```


Translation text data often uses inline formatting, in the form of tokens `{type:key:extra}`, example:
```yaml
strings:
    title: Strings
    content: "a sequence of characters, different from {link:variables:#variables}."
    variables: Variables
```
The text that would actually show on the page is the value of `variables` key (the sibling of `content`)  
These value usually do not need to be translated, but depending on language translating them makes more sense.  
If possible please do not modify tokens directly, you can move them if needed,  
If modifying tokens is necessary please read [Token Format](#token-format) below

## Token Format
When modifying tokens or keys avoid using hyphens; use underscores or camelCase instead.

```{type:key:extra}```

```
type   > Resolver name (determines what is rendered)
key    > Lookup key or value passed to the resolver
         The key always uses the key from the same section
extra  > Optional modifier (id, class, color, URL, etc.)
```

### Examples:

```yaml
strings:
    title: Strings
    content: |
        A sequence of characters, 
        different from {link:var:#variables}
    var: Variables
```
In this example, `link` is the type of token,  
`var` is a key from the same section (in this case `strings:`), will get the value of that key and insert it,  
and `#variables` is the extra argument, in this case (link type) the extra argument are used for href.  
So in HTML, it is parsed to:
```html
<a href="#variables">Variables</a>
```

### List of Supported Tokens:

```yaml
{br}                    > Line break
<br>

{link:docs}             > Link using key "docs".
{link:docs:https://...} > Link with explicit URL
{link:docs:#...}        > Link with hash link
<a href="{extra}">{docs Value}</a>

{code:docs}             > Plain <code> element
{code:docs:yel}         > <code> with class of 'yel'
<code class="{extra}">{docs Value}</code>
list of common class
yel = Highlight the text in yellow
variable = apply mindustry font, black background, light blue text

{b:docs}                > Bold
<b>{docs Value}<b>

{hl:docs:yel}           > Highlight docs in yellow
<span style="color:yellow;">{docs Value}</span>

{img:link:class}        > Insert an image
                          Image token doesn't need a key
                          link will be directly taken from :link:
<img src="{link}" class={class}>

{raw:<tag>}             > Insert raw HTML element

{delete:0:0}            > Deletes element
                          the first number indicates how many levels up the element to delete, default 0 means delete the element itself
                          the second number indicates how many siblings to also delete, default 0 means only delete the element itself
{delete:0:3 cascade}    > Deletes element and 3 next siblings, cascade means deletes in-between siblings as well
{delete:0:-3 cascade}   > Deletes element and 3 previous siblings, cascade means deletes in-between siblings as well
The delete token should be ignored when translating normally, this token is purely for restructuring the document on version changes

```