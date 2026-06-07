
# Commands

## Basic Commands 

The simplest commands are : **"Generate Text!"** and **"Generate Text (use Metadata).**"

- ### [Generate Text](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+Text)
    
- ### [Generate Text and Use Metadata](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+Text+and+Use+Metadata)
    

## OpenAI Utility Commands 

- ### [Max Token Configuration](https://docs.text-gen.com/_notes/old/commands/Set+Max+Content+Size)
    
- ### [Choose a model](https://docs.text-gen.com/_notes/old/general/Choose+a+model)
    
- ### [Estimate tokens for the current document](https://docs.text-gen.com/_notes/2-+Options/Commands/Estimate+tokens+for+the+current+document)
    

## Template commands 

For more information about see [00 Introduction To Templates](https://docs.text-gen.com/_notes/3-+Templates/00+Introduction+To+Templates).

- ### [Template Package Manager](https://docs.text-gen.com/_notes/old/templates/Template+Package+Manager)
    
- ### [Create a Template](https://docs.text-gen.com/_notes/old/templates/Create+a+Template)
    
- ### [Insert a Template](https://docs.text-gen.com/_notes/old/templates/Insert+a+Template)
    
- ### [Create a New File From Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Create+a+New+File+From+Template)
    
- ### [Generate And Insert Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+And+Insert+Template)
    
- ### [Generate and Create a New File From Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+and+Create+a+New+File+From+Template)
    
- ### [Generate & Copy To Clipboard](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+%26+Copy+To+Clipboard)
    
- ### [Estimate tokens for a template](https://docs.text-gen.com/_notes/old/templates/Estimate+tokens+for+a+template)
    

## Prerequisites

- [Considered Context](https://docs.text-gen.com/_notes/old/general/Considered+Context).
- [Hotkeys in Obsidian](https://docs.text-gen.com/_notes/old/general/Hotkeys+in+Obsidian)
- [Considered Context](https://docs.text-gen.com/_notes/old/general/Considered+Context)


---

# substring


substring allows you to take a substring of text.  
To use this function, simply use the following syntax in a template file:  
{% raw %}

```
{{{substring var startPosition endPosition}}}
```

{% endraw %}  
For example, if you only want the first 100 characters of the selected text, you would use:

{% raw %}

```
{{{substring selection 0 99}}}
```

{% endraw %}

---

Plugins:

Copilot
Text Generator



if you want to use "copilot-custom-prompts", you can call the prompts like this:

/Emojify.md


---


TextGenerator plugin commands:

# Basic Commands 

- [Generate Text](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+Text)
- [Generate Text and Use Metadata](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+Text+and+Use+Metadata)
- [Generate & Copy To Clipboard](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+%26+Copy+To+Clipboard)

# Template Commands 

- [Generate And Insert Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+And+Insert+Template)
- [Generate and Create a New File From Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Generate+and+Create+a+New+File+From+Template)
- [Batch Template Running](https://docs.text-gen.com/_notes/2-+Options/Commands/Batch+Template+Running)
- [Create a New File From Template](https://docs.text-gen.com/_notes/2-+Options/Commands/Create+a+New+File+From+Template)


# Configuration Commands 

- [Choose a LLM](https://docs.text-gen.com/_notes/2-+Options/Commands/Choose+a+LLM)

# Tools 

- [Estimate tokens for the current document](https://docs.text-gen.com/_notes/2-+Options/Commands/Estimate+tokens+for+the+current+document)
- [Template Playground](https://docs.text-gen.com/_notes/2-+Options/Tools/Template+Playground)
- [Template As A Tool](https://docs.text-gen.com/_notes/2-+Options/Tools/Template+As+A+Tool)
- [Text Extractor Tool](https://docs.text-gen.com/_notes/2-+Options/Tools/Text+Extractor+Tool)