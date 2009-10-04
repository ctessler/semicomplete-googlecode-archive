
module SlashPort
  class Component
    @@subclasses = Array.new
    @@components = Array.new

    def variables
      return self.class.variables
    end

    def configs
      return self.class.configs
    end

    def get_variables(filter=nil)
      get_things(variables, filter)
    end

    def get_configs(filter=nil)
      get_things(configs, filter)
    end

    def get_things(thing, filter=nil)
      #if filter.is_a?(String)
        #filter = Regexp.new(filter)
      #elsif filter == nil
        #filter = /^./
      #end

      data = []
      #data = Hash.new { |h,k| h[k] = Hash.new }
      thing.each do |name, var|
        #next unless name =~ filter
        #entry.merge(self.send(var.method))
        result = self.send(var.method)
        if result.is_a?(Hash)
          result.each do |key,value|
            data << {
              "component" => self.class.label,
              "section" => name,
              key => value,
            }
          end
        else 
          data << {
            "component" => self.class.label,
            "section" => name,
            "value" => result,
          }
        end
      end
      return data
    end

    def path(*names)
      return [self.class.label, *names].join("/")
    end

    # See Class#inherited for what this method 
    def self.inherited(subclass)
      puts "#{subclass.name} inherits #{self.name}"
      @@subclasses << subclass

      if subclass.respond_to?(:class_initialize)
        subclass.class_initialize
      end
    end # def self.inherited

    # class-level to easily map a variable name to a method
    def self.variable(name, method, description=nil)
      if description == nil
        raise "Variable #{self.name}/#{name} has no description"
      end
      puts "#{self.name}: new variable #{name}"

      # remember: this is a class-level instance variable
      @variables[name] = Variable.new(method, description)
    end # def self.variable

    def self.multivariable(name, method, description=nil)
      if description == nil
        raise "Variable #{self.name}/#{name} has no description"
      end
      puts "#{self.name}: new multivariable #{name}"

      # remember: this is a class-level instance variable
      @variables[name] = MultiVariable.new(method, description)
    end # def self.multivariable

    # class-level to easily map a variable name to a method
    def self.config(name, method, description=nil)
      if description == nil
        raise "Config #{self.name}/#{name} has no description"
      end
      puts "#{self.name}: new config #{name}"

      # remember: this is a class-level instance variable
      @configs[name] = Variable.new(method, description)
    end # def self.config

    def self.multiconfig(name, method, description=nil)
      if description == nil
        raise "Config #{self.name}/#{name} has no description"
      end
      puts "#{self.name}: new multiconfig #{name}"

      # remember: this is a class-level instance variable
      @configs[name] = MultiVariable.new(method, description)
    end # def self.multiconfig

    def self.configs(filter=nil)
      return @configs
    end

    def self.variables(filter=nil)
      return @variables
    end

    # class-level initialization. This is called when ruby first
    # creates this class object, a hack made possible by
    # overriding Class#inherited (see 'def inherited' above).
    def self.class_initialize
      puts "#{self}::class_initialize"
      # remember, this is a class-level instance variable
      @variables = Registry.new
      @configs = Registry.new
      @label = self.name.split("::")[-1].downcase
    end # def.class_initialize

    # Show me all subclasses of SlashPort::Component
    def self.components
      if @@components.length == 0
        @@subclasses.each do |klass|
          @@components << klass.new
        end
      end
      return @@components
    end # def self.components

    def self.get_things(thing, filter)
      data = []
      self.components.each do |component|
        data += component.send("get_#{thing}", filter)
      end
      return data
    end

    def self.get_variables(filter=nil)
      return self.get_things("variables", filter)
    end

    def self.get_configs(filter=nil)
      return self.get_things("configs", filter)
    end

    def self.label
      return @label
    end
  end # class Component
end # module SlashPort